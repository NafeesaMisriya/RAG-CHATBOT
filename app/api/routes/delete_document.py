from fastapi import (
    APIRouter
)

from app.retrieval.qdrant_manager import (
    QdrantManager
)

from app.utils.document_registry import (
    DocumentRegistry
)

router = APIRouter()

qdrant = (
    QdrantManager()
)


@router.delete(
    "/documents/{collection}"
)
def delete_document(
    collection: str
):

    qdrant.client.delete_collection(
        collection_name=
        collection
    )

    docs = (
        DocumentRegistry.get_documents()
    )

    docs = [
        doc
        for doc in docs
        if doc["collection"]
        != collection
    ]

    DocumentRegistry.save(
        docs
    )

    return {
        "message":
        "Document deleted."
    }