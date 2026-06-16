from app.embedding.embedding_manager import (
    EmbeddingManager
)

from app.retrieval.qdrant_manager import (
    QdrantManager
)

embedder = EmbeddingManager()

vector = embedder.embed_text(
    "hello world"
)

dimension = len(vector)

print(
    f"Dimension = {dimension}"
)

qdrant = QdrantManager()

qdrant.create_collection(
    collection_name="document_chunks",
    vector_size=len(vector)
)

print(
    qdrant.get_collection_info(
        "document_chunks"
    )
)