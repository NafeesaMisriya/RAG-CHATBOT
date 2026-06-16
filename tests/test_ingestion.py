from app.ingestion.document_ingestor import (
    DocumentIngestor
)

ingestor = (
    DocumentIngestor()
)

ingestor.ingest(
    pdf_path=
    "data/raw/Biology.pdf",

    collection_name=
    "documents"
)