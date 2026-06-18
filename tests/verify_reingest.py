"""Re-ingest image/OCR test PDFs cleanly and verify the new behaviour:
cross-PDF image isolation, image OCR, and per-collection image paths."""

import os
from pathlib import Path

from app.retrieval.qdrant_manager import QdrantManager
from app.ingestion.document_ingestor import DocumentIngestor
from app.utils.document_registry import DocumentRegistry

TEST_PDFS = [
    "ocr_vision_test_document.pdf",
    "real_image_test_pdf.pdf",
    "ocr_local_image_test.pdf",
    "ocr_single_page_test.pdf",
]


def collection_for(name):
    return (
        name.replace(".pdf", "")
        .replace(" ", "_")
        .lower()
    )


def main():
    qdrant = QdrantManager()

    existing = [
        c.name
        for c in qdrant.list_collections().collections
    ]

    for pdf in TEST_PDFS:
        pdf_path = os.path.join("data/uploads", pdf)
        coll = collection_for(pdf)

        if not os.path.exists(pdf_path):
            print(f"SKIP (missing file): {pdf}")
            continue

        if coll in existing:
            print(f"\nDeleting existing collection: {coll}")
            qdrant.delete_collection(coll)

        print(f"\n=== Re-ingesting {pdf} -> {coll} ===")
        DocumentIngestor().ingest(
            pdf_path=pdf_path,
            collection_name=coll,
        )
        DocumentRegistry.register(pdf, coll)

    print("\n\n========== VERIFICATION ==========\n")

    for pdf in TEST_PDFS:
        pdf_path = os.path.join("data/uploads", pdf)
        if not os.path.exists(pdf_path):
            continue
        coll = collection_for(pdf)

        # 1. Per-collection image dir isolation
        img_dir = Path("data/extracted/images") / coll
        imgs = (
            list(img_dir.glob("*"))
            if img_dir.exists()
            else []
        )
        print(f"[{coll}]")
        print(f"  image dir: {img_dir}  exists={img_dir.exists()}  files={len(imgs)}")

        # 2. Inspect stored image points: path namespacing + OCR text
        try:
            points = qdrant.client.scroll(
                collection_name=coll,
                limit=200,
                with_payload=True,
            )[0]
        except Exception as e:
            print(f"  scroll error: {e}")
            continue

        image_points = [
            p for p in points
            if p.payload.get("metadata", {}).get("node_type") == "image"
        ]
        print(f"  total points={len(points)}  image points={len(image_points)}")

        for p in image_points[:3]:
            meta = p.payload.get("metadata", {})
            path = meta.get("image_path", "")
            isolated = f"images/{coll}/" in path.replace("\\", "/")
            has_ocr = "IMAGE TEXT:" in (p.payload.get("content") or "")
            print(f"    path={path}")
            print(f"      isolated_to_collection={isolated}  has_ocr_text={has_ocr}")
            print(f"      content={ (p.payload.get('content') or '')[:160]!r}")

        print()


if __name__ == "__main__":
    main()
