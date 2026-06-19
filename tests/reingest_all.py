"""Re-ingest specific documents.

Usage:
  ./venv/Scripts/python.exe -m tests.reingest_all biology_txt chemistry
  ./venv/Scripts/python.exe -m tests.reingest_all english
  ./venv/Scripts/python.exe -m tests.reingest_all  # runs ALL if no args

Available collections: biology_txt, chemistry, english, real_image_test_pdf
"""
import sys
from app.retrieval.qdrant_manager import QdrantManager
from app.ingestion.document_ingestor import DocumentIngestor

ALL_DOCS = {
    "biology_txt":        "data/uploads/Biology_txt.pdf",
    "chemistry":          "data/uploads/Chemistry.pdf",
    "english":            "data/uploads/English.pdf",
    "real_image_test_pdf":"data/uploads/real_image_test_pdf.pdf",
}

targets = sys.argv[1:] if len(sys.argv) > 1 else list(ALL_DOCS.keys())

unknown = [t for t in targets if t not in ALL_DOCS]
if unknown:
    print(f"Unknown collection(s): {unknown}")
    print(f"Available: {list(ALL_DOCS.keys())}")
    sys.exit(1)

qm = QdrantManager()
ingestor = DocumentIngestor()
existing = [c.name for c in qm.list_collections().collections]

for collection in targets:
    pdf = ALL_DOCS[collection]
    if collection in existing:
        print(f"\n=== Deleting '{collection}' ===")
        qm.delete_collection(collection)
    print(f"\n=== Ingesting '{collection}' from {pdf} ===")
    ingestor.ingest(pdf_path=pdf, collection_name=collection)
    print(f"=== DONE: {collection} ===")

print("\n=== RE-INGEST COMPLETE ===")
