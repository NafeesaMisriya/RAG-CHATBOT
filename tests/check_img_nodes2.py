import sys
sys.path.insert(0, ".")
from app.retrieval.qdrant_manager import QdrantManager
from qdrant_client.models import Filter, FieldCondition, MatchValue

qm = QdrantManager()

for col in ["real_image_test_pdf", "biology_txt"]:
    print(f"\n===== {col} =====")
    try:
        pts, _ = qm.client.scroll(
            collection_name=col,
            scroll_filter=Filter(must=[FieldCondition(key="metadata.node_type", match=MatchValue(value="image"))]),
            limit=20, with_payload=True, with_vectors=False
        )
        print(f"Image nodes: {len(pts)}")
        for pt in pts[:5]:
            p = pt.payload or {}
            meta = p.get("metadata", {}) or {}
            content = p.get("content", "")
            page = p.get("page")
            path = (meta.get("image_path") or "")[-35:]
            has_fig = content.startswith("FIGURE:")
            fig_text = content[:120] if has_fig else "(no FIGURE: prefix)"
            print(f"  Page {page} | {path}")
            print(f"  Content: {fig_text!r}")
    except Exception as e:
        print(f"  ERROR: {e}")
