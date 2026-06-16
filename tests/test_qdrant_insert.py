import uuid

from app.embedding.embedding_manager import (
    EmbeddingManager
)

from app.models.vector_record import (
    VectorRecord
)

from app.retrieval.qdrant_manager import (
    QdrantManager
)

embedder = EmbeddingManager()

vector = embedder.embed_text(
    "Photosynthesis converts light energy into chemical energy."
)

record = VectorRecord(
    chunk_id=str(uuid.uuid4()),

    vector=vector,

    content=
    "Photosynthesis converts light energy into chemical energy.",

    page=1,

    source_document=
    "test.pdf"
)

qdrant = QdrantManager()

qdrant.insert_vectors(
    collection_name=
    "document_chunks",

    vector_records=
    [record]
)

print(
    qdrant.count_points(
        "document_chunks"
    )
)