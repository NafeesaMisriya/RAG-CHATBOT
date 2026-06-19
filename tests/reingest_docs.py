"""Re-ingest chemistry + english with figure-context enrichment.

Run: ./venv/Scripts/python.exe -m tests.reingest_docs
"""
from app.retrieval.qdrant_manager import QdrantManager
from app.ingestion.document_ingestor import DocumentIngestor

DOCS = [
    ("data/uploads/Chemistry.pdf", "chemistry"),
    ("data/uploads/English.pdf", "english"),
]

qm = QdrantManager()
ingestor = DocumentIngestor()

for pdf, collection in DOCS:
    existing = [c.name for c in qm.list_collections().collections]
    if collection in existing:
        print(f"\n=== Deleting existing '{collection}' ===")
        qm.delete_collection(collection)
    print(f"=== Ingesting '{collection}' from {pdf} ===")
    ingestor.ingest(pdf_path=pdf, collection_name=collection)
    print(f"=== DONE: {collection} ===")

print("\nALL RE-INGEST COMPLETE")
