from fastapi import APIRouter

from app.utils.document_registry import (
    DocumentRegistry
)

router = APIRouter()


@router.get("/documents")
def documents():

    return (
        DocumentRegistry
        .get_documents()
    )