# tests/test_qdrant_connection.py

from app.retrieval.qdrant_manager import (
    QdrantManager
)

qdrant = QdrantManager()

print(
    qdrant.list_collections()
)