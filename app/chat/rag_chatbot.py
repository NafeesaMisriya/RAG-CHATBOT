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

                limit=5
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

        for context in contexts[:5]:

            print(
                f"Page: "
                f"{context['page']} | "
                f"Score: "
                f"{context['rerank_score']:.4f}"
            )

        # Keep existing behaviour:
        # use only highest-ranked chunk

        if contexts:

            contexts = [
                contexts[0]
            ]

        return contexts

    def ask(
        self,
        question,
        collection_name,
        history=None
    ):

        if history is None:

            history = []

        contexts = (
            self._get_contexts(
                question=
                question,

                collection_name=
                collection_name,

                history=
                history
            )
        )
        
        answer = (
            self.generator.generate(
                query=
                question,

                contexts=
                contexts,

                history=
                history
            )
        )

        return {
            "answer":
            answer,

            "sources":
            contexts
        }

    def stream_answer(
        self,
        question,
        collection_name,
        history=None
    ):

        if history is None:

            history = []

        contexts = (
            self._get_contexts(
                question=
                question,

                collection_name=
                collection_name,

                history=
                history
            )
        )
        yield from (
            self.generator.stream_generate(
                query=
                question,

                contexts=
                contexts,

                history=
                history
            )
        )