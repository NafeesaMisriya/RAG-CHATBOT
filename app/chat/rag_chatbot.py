from app.retrieval.retriever import (
    Retriever
)

from app.reranking.reranker import (
    Reranker
)

from app.generation.generator import (
    Generator
)

from app.query_rewriting.query_rewriter import (
    QueryRewriter
)


# Image selection.
#
# Image captions are too thin to surface reliably through vector search
# (e.g. "the human brain and spinal"), so figures are NOT discovered by
# caption similarity. Instead they are discovered by PAGE: we take the
# pages the answer is actually grounded in (the top-ranked text hits with
# a positive rerank score), pull every image node on those pages directly
# from Qdrant, then rerank those figures against the query so the one
# related to the question wins (the labelled brain diagram for a brain
# question) and unrelated figures are dropped. If no page is grounded
# (an out-of-context query), no images are shown.

# Relevance gate.
#
# The cross-encoder's absolute rerank score is NOT comparable across
# documents: clean text scores around 0 when relevant, while scanned/OCR
# text scores deeply negative even when relevant. So an absolute floor
# wrongly rejects every result in a scanned PDF. Instead we use a RELATIVE
# signal: a query is "grounded" when its best hit stands out from the
# spread of retrieved results. Off-topic queries produce a flat, uniformly
# low distribution (small gap); relevant queries produce a clear peak
# (large gap) regardless of the absolute baseline.
GROUNDING_GAP = 1.5

# How many distinct grounded pages to pull figures from (hard cap).
MAX_ANCHOR_PAGES = 3

# A page only counts as an anchor if its text rerank score is within this
# margin of the BEST page's score. This keeps figures tied to the page the
# answer is really about: when one page dominates (e.g. the brain page at
# 3.9 vs the next at 0.2) only that page anchors, so unrelated figures on
# weakly-ranked pages are not pulled in. When several pages are comparably
# relevant (e.g. a bare "show all the images" request, where every page
# scores about the same) they all anchor.
ANCHOR_SCORE_MARGIN = 2.0

# Keep figures whose rerank score is within this margin of the best
# figure, so only figures related to the query survive.
IMAGE_RELEVANCE_MARGIN = 2.0

# For a normal query, a figure is only shown if it is clearly the most
# relevant on the page: the top figure must beat the second by at least
# this margin. When several figures on a page score almost the same
# (flat), the weak captions give no signal about which is relevant, so we
# show nothing rather than guess (e.g. a person query landing on a page of
# unrelated diagrams). A page with a single figure is exempt.
IMAGE_STANDOUT_MARGIN = 1.5

# Max images returned: default vs an explicit "show all images" request.
MAX_IMAGES = 3
MAX_IMAGES_EXPLICIT = 8

# Max source citations to display. Only the sources that actually answer
# the query are shown (relevance-gated below), not every retrieved chunk.
MAX_SOURCES = 2

# Words that signal the user explicitly wants figures.
_IMAGE_WORDS = (
    "image", "images", "picture", "pictures", "figure", "figures",
    "diagram", "diagrams", "illustration", "illustrations",
    "photo", "photos", "visual", "visuals", "drawing", "drawings"
)

# Words that, alongside an image word, signal "give me all of them".
_ALL_WORDS = ("all", "every", "each", "both", "list", "show")


# The generator emits this exact sentence when the question is not
# answerable from the document. When the answer is this refusal we must
# not show figures or sources — they would contradict "not found".
_REFUSAL_MARKER = "could not find the answer"


def _is_refusal(answer):

    return _REFUSAL_MARKER in (answer or "").lower()


# Captions BLIP assigns to decorative page chrome (sticky-note graphics,
# blank framed boxes) that are not real content figures. Such images are
# never useful answers, so they are dropped before figure selection.
_DECORATIVE_MARKERS = (
    "sticky note",
    "note paper",
    "blank paper",
    "blank page",
    "blank sheet",
)


def _is_decorative(content):

    text = (content or "").lower()

    return any(
        marker in text
        for marker in _DECORATIVE_MARKERS
    )


def _to_file_url(path):

    """Convert a stored data-relative file path into the URL served by
    the FastAPI static mount at '/files'. Returns None if the path does
    not live under the 'data/' directory."""

    if not path:

        return None

    normalized = path.replace("\\", "/")

    marker = "data/"

    index = normalized.find(marker)

    if index == -1:

        return None

    relative = normalized[index + len(marker):]

    return f"/files/{relative}"


class RAGChatbot:

    def __init__(self):

        self.retriever = (
            Retriever()
        )

        self.reranker = (
            Reranker()
        )

        self.generator = (
            Generator()
        )

        self.query_rewriter = (
            QueryRewriter()
        )

    def _deduplicate_sources(
        self,
        contexts
    ):

        seen = set()

        unique = []

        for context in contexts:

            if (
                context.get("node_type")
                ==
                "image"
            ):
                continue

            key = (
                context.get("page"),
                context.get(
                    "source_document"
                )
            )

            if key in seen:
                continue

            seen.add(key)

            unique.append(
                context
            )

        return unique

    def _build_source(
        self,
        context
    ):

        """Shape a retrieved context into a citation payload, including a
        clickable link to the source PDF at the relevant page."""

        page = context.get("page")

        source_url = _to_file_url(
            context.get("source_document")
        )

        if source_url and page:

            source_url = (
                f"{source_url}#page={page}"
            )

        return {
            "title":
            context.get("title"),

            "page":
            page,

            "content":
            context.get("content"),

            "source_document":
            context.get("source_document"),

            "source_url":
            source_url
        }

    def _mentions_images(
        self,
        question
    ):

        """True when the query explicitly references figures at all."""

        q = (question or "").lower()

        return any(
            word in q
            for word in _IMAGE_WORDS
        )

    def _wants_all_images(
        self,
        question
    ):

        """True when the user explicitly asks for (all) figures, e.g.
        'show all the diagrams' or 'list the images'."""

        if not self._mentions_images(question):

            return False

        q = (question or "").lower()

        return any(
            word in q
            for word in _ALL_WORDS
        )

    def _is_grounded(
        self,
        text_contexts
    ):

        """Relative relevance gate: True when the best text hit stands out
        from the spread of retrieved results. Robust across clean and
        scanned PDFs because it compares scores WITHIN this query's results
        rather than to a fixed absolute threshold."""

        if not text_contexts:

            return False

        scores = [
            context.get("rerank_score", 0.0)
            for context in text_contexts
        ]

        return (max(scores) - min(scores)) >= GROUNDING_GAP

    def _select_sources(
        self,
        contexts
    ):

        """Show only the citations that actually answer the query.

        Nothing is cited for an out-of-context query (relative grounding
        gate). Otherwise sources are deduplicated by page and kept only
        while within ANCHOR_SCORE_MARGIN of the best source, so a query
        answered by one page cites just that page (not the next two
        loosely-retrieved chunks)."""

        deduped = self._deduplicate_sources(
            contexts
        )

        if not deduped:

            return []

        if not self._is_grounded(deduped):

            return []

        top_score = deduped[0].get(
            "rerank_score",
            0.0
        )

        selected = []

        for context in deduped:

            score = context.get("rerank_score", 0.0)

            if top_score - score > ANCHOR_SCORE_MARGIN:
                break

            selected.append(
                self._build_source(context)
            )

            if len(selected) >= MAX_SOURCES:
                break

        return selected

    def _anchor_pages(
        self,
        contexts,
        relax=False,
        broad=False
    ):

        """Pages the answer is grounded in: the distinct pages of the
        top-ranked TEXT hits.

        For normal questions a relevance gate applies (the relative
        grounding signal), so an out-of-context query surfaces no figures.
        When the user explicitly asks for figures (relax=True) the gate is
        dropped and we anchor to the top pages, because an instruction like
        'show the diagrams' scores low as plain text yet still targets the
        most relevant pages."""

        if not contexts:

            return []

        text_contexts = [
            context
            for context in contexts
            if context.get("node_type") != "image"
        ]

        if not text_contexts:

            return []

        # Out-of-context guard for normal questions. Skipped when the user
        # explicitly asks for figures (relax=True).
        if not relax and not self._is_grounded(text_contexts):

            return []

        top_score = text_contexts[0].get(
            "rerank_score",
            0.0
        )

        pages = []

        # text_contexts are sorted by rerank score (best first), so once a
        # page falls outside the margin every later page does too. In broad
        # mode (an explicit "show all images" request) the margin is
        # ignored and we simply take the top pages up to the cap.
        for context in text_contexts:

            score = context.get("rerank_score", 0.0)

            if not broad and top_score - score > ANCHOR_SCORE_MARGIN:
                break

            page = context.get("page")

            if page is None or page in pages:
                continue

            pages.append(page)

            if len(pages) >= MAX_ANCHOR_PAGES:
                break

        return pages

    def _select_images(
        self,
        question,
        contexts,
        collection_name
    ):

        """Pick the figures related to the query.

        Figures are discovered by page (the grounded pages), pulled from
        Qdrant, then reranked against the query so the related figure wins
        and unrelated ones are dropped."""

        wants_all = self._wants_all_images(question)

        # The relevance gate is bypassed ONLY for an explicit "show all the
        # images" browse request (which has no topic to ground on). A
        # topical image request like "image of brain" still must ground —
        # otherwise an off-topic query surfaces a random figure.
        pages = self._anchor_pages(
            contexts,
            relax=wants_all,
            broad=wants_all
        )

        if not pages:

            return []

        image_contexts = (
            self.retriever.qdrant.get_image_nodes_by_pages(
                collection_name=collection_name,
                pages=pages
            )
        )

        image_contexts = [
            context
            for context in image_contexts
            if context.get("image_path")
            and not _is_decorative(context.get("content"))
        ]

        if not image_contexts:

            return []

        # Rank the candidate figures by relevance to the query (caption
        # vs query) so the labelled brain diagram beats an unrelated
        # figure that merely shares the page.
        image_contexts = (
            self.reranker.rerank(
                query=question,
                contexts=image_contexts
            )
        )

        image_contexts.sort(
            key=lambda c: c.get(
                "rerank_score",
                float("-inf")
            ),
            reverse=True
        )

        cap = (
            MAX_IMAGES_EXPLICIT
            if wants_all
            else MAX_IMAGES
        )

        best_score = image_contexts[0].get(
            "rerank_score",
            0.0
        )

        # Normal query precision gate: show a figure only when it is clearly
        # the most relevant. With several near-tied figures the captions
        # give no signal, so show nothing instead of a random one. A single
        # figure on the grounded page is taken as-is.
        if not wants_all:

            if len(image_contexts) > 1:

                second_score = image_contexts[1].get(
                    "rerank_score",
                    0.0
                )

                if best_score - second_score < IMAGE_STANDOUT_MARGIN:

                    return []

            image_contexts = image_contexts[:1]

        images = []

        seen = set()

        for context in image_contexts:

            score = context.get(
                "rerank_score",
                0.0
            )

            # Normal queries are already trimmed to the standout figure
            # above; an explicit "show all" request returns every figure on
            # the grounded pages (up to the cap). So no further filtering
            # here — just dedupe and cap.

            image_path = context.get("image_path")

            if not image_path or image_path in seen:
                continue

            seen.add(image_path)

            images.append(
                {
                    "page":
                    context.get("page"),

                    "image_path":
                    image_path,

                    "image_url":
                    _to_file_url(
                        image_path
                    ),

                    "rerank_score":
                    score
                }
            )

            if len(images) >= cap:
                break

        return images

    def _get_contexts(
        self,
        question,
        collection_name,
        history
    ):

        retrieval_query = (
            self.query_rewriter.rewrite(
                question,
                history
            )
        )

        print(
            "\nRetrieval Query:",
            retrieval_query
        )

        contexts = (
            self.retriever.retrieve(
                query=
                retrieval_query,

                collection_name=
                collection_name,

                limit=30
            )
        )

        contexts = (
            self.reranker.rerank(
                query=
                retrieval_query,

                contexts=
                contexts
            )
        )

        print(
            "\nTop Rerank Scores:"
        )

        for context in contexts[:10]:

            print(
                f"Page: "
                f"{context['page']} | "
                f"Score: "
                f"{context['rerank_score']:.4f}"
            )

        return contexts

    def _prepare(
        self,
        question,
        collection_name,
        history
    ):

        """Single retrieval entry point. Runs retrieval + rerank exactly
        once and derives every downstream view (generation context,
        citations, images) from that one result set."""

        retrieved_contexts = (
            self._get_contexts(
                question=
                question,

                collection_name=
                collection_name,

                history=
                history
            )
        )

        generation_contexts = (
            retrieved_contexts[:8]
        )

        source_contexts = (
            self._select_sources(
                retrieved_contexts
            )
        )

        image_sources = (
            self._select_images(
                question=question,
                contexts=retrieved_contexts,
                collection_name=collection_name
            )
        )

        return (
            generation_contexts,
            source_contexts,
            image_sources
        )

    def ask(
        self,
        question,
        collection_name,
        history=None
    ):

        if history is None:

            history = []

        (
            generation_contexts,
            source_contexts,
            image_sources
        ) = self._prepare(
            question=question,
            collection_name=collection_name,
            history=history
        )

        answer = (
            self.generator.generate(
                query=
                question,

                contexts=
                generation_contexts,

                history=
                history
            )
        )

        # If the model couldn't answer from the document, don't attach
        # figures or sources — they would contradict the refusal.
        if _is_refusal(answer):

            source_contexts = []

            image_sources = []

        return {

            "answer":
            answer,

            "sources":
            source_contexts,

            "images":
            image_sources
        }

    def stream_answer(
        self,
        question,
        collection_name,
        history=None
    ):

        """Yields structured events for a single SSE stream:

            {"type": "token",   "data": "<text chunk>"}
            {"type": "sources", "data": [...]}
            {"type": "images",  "data": [...]}

        Retrieval happens once; the answer and its metadata travel over
        the same stream so the client never needs a second request."""

        if history is None:

            history = []

        (
            generation_contexts,
            source_contexts,
            image_sources
        ) = self._prepare(
            question=question,
            collection_name=collection_name,
            history=history
        )

        full_answer = ""

        for chunk in (
            self.generator.stream_generate(
                query=
                question,

                contexts=
                generation_contexts,

                history=
                history
            )
        ):

            full_answer += chunk

            yield {
                "type": "token",
                "data": chunk
            }

        # If the model couldn't answer from the document, suppress figures
        # and sources so they don't contradict the refusal.
        if _is_refusal(full_answer):

            source_contexts = []

            image_sources = []

        yield {
            "type": "sources",
            "data": source_contexts
        }

        yield {
            "type": "images",
            "data": image_sources
        }
