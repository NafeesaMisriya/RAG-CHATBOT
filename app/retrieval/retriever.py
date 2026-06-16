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

    def retrieve(
        self,
        query: str,
        collection_name: str,
        limit: int = 5
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

                limit=limit
            )
        )

        contexts = []

        for point in results.points:

            contexts.append(
                {
                    
                    "content":
                    point.payload["content"],

                    "page":
                    point.payload["page"],

                    "source_document":
                    point.payload["source_document"],

                    "score":
                    point.score
                }
            )
                
        return contexts