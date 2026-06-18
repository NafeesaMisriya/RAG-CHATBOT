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
# The ms-marco cross-encoder scores short image captions very low in
# absolute terms (almost always negative), so an absolute score floor
# wrongly discards relevant images. Instead we anchor on the page of
# the single most relevant retrieved context: the figure that belongs
# with the answer sits on the same page the answer is drawn from. Among
# the images on that page we keep the best one(s), allowing extras only
# if their score is within IMAGE_PAGE_MARGIN of the best image (so a
# page with several genuinely relevant figures still shows them, while
# an unrelated figure sharing the page is dropped).
IMAGE_PAGE_MARGIN = 1.5

# Max images returned with a single answer.
MAX_IMAGES = 3


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

    def _filter_images(
        self,
        contexts
    ):

        if not contexts:

            return []

        # Anchor on the page of the most relevant retrieved context.
        primary_page = contexts[0].get("page")

        # Collect images that live on that page, best score first.
        candidates = [
            context
            for context in contexts
            if context.get("node_type") == "image"
            and context.get("image_path")
            and context.get("page") == primary_page
        ]

        candidates.sort(
            key=lambda c: c.get(
                "rerank_score",
                float("-inf")
            ),
            reverse=True
        )

        if not candidates:

            return []

        best_score = (
            candidates[0].get(
                "rerank_score",
                0.0
            )
        )

        images = []

        seen = set()

        for context in candidates:

            score = context.get(
                "rerank_score",
                0.0
            )

            # Keep figures close to the best image on this page; drop an
            # unrelated figure that merely shares the page.
            if (
                best_score - score
                >
                IMAGE_PAGE_MARGIN
            ):
                continue

            image_path = context.get(
                "image_path"
            )

            if image_path in seen:
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

        return images[:MAX_IMAGES]

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

        source_contexts = [
            self._build_source(context)
            for context in
            self._deduplicate_sources(
                retrieved_contexts
            )[:3]
        ]

        image_sources = (
            self._filter_images(
                retrieved_contexts
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

            yield {
                "type": "token",
                "data": chunk
            }

        yield {
            "type": "sources",
            "data": source_contexts
        }

        yield {
            "type": "images",
            "data": image_sources
        }
