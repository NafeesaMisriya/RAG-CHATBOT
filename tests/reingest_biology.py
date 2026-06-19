"""One-off: re-ingest biology_txt with the upgraded (BLIP-large) captioner.

Run: ./venv/Scripts/python.exe -m tests.reingest_biology
"""
from app.retrieval.qdrant_manager import QdrantManager
from app.ingestion.document_ingestor import DocumentIngestor

PDF = "data/uploads/Biology_txt.pdf"
COLLECTION = "biology_txt"

qm = QdrantManager()

existing = [c.name for c in qm.list_collections().collections]
if COLLECTION in existing:
    print(f"Deleting existing collection '{COLLECTION}'...")
    qm.delete_collection(COLLECTION)
else:
    print(f"Collection '{COLLECTION}' not present; fresh ingest.")

print("Starting ingestion (BLIP-large)...")
DocumentIngestor().ingest(pdf_path=PDF, collection_name=COLLECTION)
print("RE-INGEST COMPLETE")
