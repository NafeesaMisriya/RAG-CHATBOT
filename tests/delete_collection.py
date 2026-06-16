from app.retrieval.qdrant_manager import (
    QdrantManager
)

qdrant = QdrantManager()

qdrant.client.delete_collection(
    collection_name="documents"
)
"""

# tests/test_collection_info.py

from app.retrieval.qdrant_manager import (
    QdrantManager
)

q = QdrantManager()

info = q.client.get_collection(
    "documents"
)

print(
    info.points_count
)"""