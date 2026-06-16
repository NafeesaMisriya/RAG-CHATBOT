from app.embedding.embedding_manager import (
    EmbeddingManager
)

from app.retrieval.qdrant_manager import (
    QdrantManager
)

embedder = EmbeddingManager()

query_vector = embedder.embed_text(
    "photosynthesis"
)

qdrant = QdrantManager()

results = qdrant.search(
    collection_name="document_chunks",
    query_vector=query_vector,
    limit=5
)

print(results)