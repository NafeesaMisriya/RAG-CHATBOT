import os
from app.retrieval.retriever import (
    Retriever
)

from app.generation.generator import (
    Generator
)

from app.chat.memory import (
    ConversationMemory
)

from app.reranking.reranker import (
    Reranker
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

        self.memory = (
            ConversationMemory()
        )

        self.rewriter = (
            QueryRewriter()
        )

    def ask(
        self,
        question,
        collection_name="documents"
    ):

        # Store user message
        self.memory.add_message(
            "user",
            question
        )

        history = (
            self.memory.get_history()
        )

        # Rewrite follow-up questions
        retrieval_query = (
            self.rewriter.rewrite(
                question,
                history
            )
        )

        print(
            f"\nRetrieval Query: "
            f"{retrieval_query}"
        )

        # Retrieve more candidates
        contexts = (
            self.retriever.retrieve(
                query=retrieval_query,
                collection_name=collection_name,
                limit=10
            )
        )

        # Rerank retrieved chunks
        contexts = (
            self.reranker.rerank(
                query=retrieval_query,
                contexts=contexts,
                top_k=3
            )
        )

        if not contexts:

            return {
                "answer":
                "I could not find relevant information in the document.",
                "sources": []
            }

        # Generate answer
        answer = (
            self.generator.generate(
                query=question,
                contexts=contexts,
                history=history
            )
        )

        # Save assistant response
        self.memory.add_message(
            "assistant",
            answer
        )

        # Build source list
        sources = []

        for context in contexts:

            pdf_path = (
                context["source_document"]
            )

            page = (
                context["page"]
            )

            pdf_link = (
                f"{pdf_path}#page={page}"
            )

            sources.append(
                {
                    "page": page,

                    "document":
                    os.path.basename(
                        pdf_path
                    ),

                    "link":
                    pdf_link,

                    "score":
                    context.get(
                        "rerank_score",
                        context.get(
                            "score",
                            0
                        )
                    )
                }
            )

        return {
            "answer":
            answer,

            "sources":
            contexts
        }