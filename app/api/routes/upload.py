import os

from fastapi import (
    APIRouter,
    UploadFile,
    File
)

from app.ingestion.document_ingestor import (
    DocumentIngestor
)

from app.utils.document_registry import (
    DocumentRegistry
)

router = APIRouter()


@router.post(
    "/upload"
)
async def upload_pdf(
    file: UploadFile = File(...)
):

    documents = (
        DocumentRegistry.get_documents()
    )

    already_exists = any(
        doc["name"] ==
        file.filename
        for doc in documents
    )

    if already_exists:

        return {
            "message":
            "Document already exists."
        }

    os.makedirs(
        "data/uploads",
        exist_ok=True
    )

    pdf_path = os.path.join(
        "data/uploads",
        file.filename
    )

    content = (
        await file.read()
    )

    with open(
        pdf_path,
        "wb"
    ) as f:

        f.write(
            content
        )

    collection_name = (
        file.filename
        .replace(".pdf", "")
        .replace(" ", "_")
        .lower()
    )

    ingestor = (
        DocumentIngestor()
    )

    ingestor.ingest(
        pdf_path=pdf_path,
        collection_name=
        collection_name
    )

    DocumentRegistry.register(
        document_name=
        file.filename,

        collection_name=
        collection_name
    )

    return {
        "message":
        "Document uploaded successfully",

        "collection":
        collection_name
    }