from app.embedding.embedding_manager import (
    EmbeddingManager
)

from app.retrieval.qdrant_manager import (
    QdrantManager
)


class Retriever:

    def __init__(self):

        self.embedder = (
            EmbeddingManager()
        )

        self.qdrant = (
            QdrantManager()
        )

    def _apply_keyword_boost(
        self,
        query,
        contexts
    ):

        query_words = set(
            query.lower().split()
        )

        for context in contexts:

            boost = 0

            content = (
                context["content"]
                .lower()
            )

            metadata = (
                context.get(
                    "metadata",
                    {}
                )
            )

            title = str(
                metadata.get(
                    "title",
                    ""
                )
            ).lower()

            unit = str(
                metadata.get(
                    "unit",
                    ""
                )
            ).lower()

            # Title boost

            for word in query_words:

                if word in title:

                    boost += 5

            # Unit boost

            for word in query_words:

                if word in unit:

                    boost += 2

            # Exact content matches

            for word in query_words:

                if word in content:

                    boost += 0.5

            context[
                "hybrid_score"
            ] = (
                context["score"]
                + boost
            )

        contexts.sort(
            key=lambda x:
            x["hybrid_score"],
            reverse=True
        )

        return contexts

    def retrieve(
        self,
        query: str,
        collection_name: str,
        limit: int = 20
    ):

        query_vector = (
            self.embedder.embed_text(
                query
            )
        )

        results = (
            self.qdrant.search(
                collection_name=
                collection_name,

                query_vector=
                query_vector,

                limit=50
            )
        )

        contexts = []

        for point in results.points:

            metadata = (
                point.payload.get(
                    "metadata",
                    {}
                )
            )

            contexts.append(
            {
                "content":
                point.payload["content"],

                "page":
                point.payload["page"],

                "source_document":
                point.payload["source_document"],

                "score":
                point.score,

                "metadata":
                metadata,

                "title":
                metadata.get(
                    "title"
                ),

                "unit":
                metadata.get(
                    "unit"
                ),

                "node_type":
                metadata.get(
                    "node_type"
                ),

                "image_path":
                metadata.get(
                    "image_path"
                )
            }
            )
        contexts = (
            self._apply_keyword_boost(
                query,
                contexts
            )
        )

        return contexts[:limit]