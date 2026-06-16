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

    def ask(
        self,
        question,
        collection_name,
        history=None
    ):

        if history is None:

            history = []

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

        if contexts:

            contexts = [
                contexts[0]
            ]

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