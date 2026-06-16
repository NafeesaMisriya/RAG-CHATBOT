"""from app.retrieval.qdrant_manager import (
    QdrantManager
)

qdrant = QdrantManager()

qdrant.delete_collection(
    "documents"
)
"""

# tests/test_collection_info.py

from app.retrieval.qdrant_manager import (
    QdrantManager
)

qdrant = QdrantManager()

print(
    qdrant.get_collection_info(
        "documents"
    )
)