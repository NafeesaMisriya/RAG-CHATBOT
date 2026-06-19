"""Check image nodes for a collection — show pages, enrichment status, sample content."""
import sys
sys.path.insert(0, ".")

from app.retrieval.qdrant_manager import QdrantManager
from qdrant_client.models import Filter, FieldCondition, MatchValue

COLLECTION = sys.argv[1] if len(sys.argv) > 1 else "biology_txt"

qm = QdrantManager()

pts, _ = qm.client.scroll(
    collection_name=COLLECTION,
    scroll_filter=Filter(
        must=[FieldCondition(key="metadata.node_type", match=MatchValue(value="image"))]
    ),
    limit=500,
    with_payload=True,
    with_vectors=False
)

enriched = 0
plain = 0
pages = {}

for pt in pts:
    p = pt.payload or {}
    content = p.get("content", "")
    page = p.get("page")
    pages[page] = pages.get(page, 0) + 1
    if content.startswith("FIGURE:"):
        enriched += 1
    else:
        plain += 1

print(f"\nCollection: {COLLECTION}")
print(f"Total image nodes: {len(pts)}")
print(f"  With FIGURE: enrichment: {enriched}")
print(f"  Plain (no enrichment):   {plain}")
print(f"\nPages with images (page -> count):")
for pg in sorted(pages.keys(), key=lambda x: (x is None, x)):
    print(f"  Page {pg}: {pages[pg]} image(s)")

# Show samples from page 17-18 for biology
target_pages = [17, 18]
print(f"\nSample image nodes from pages {target_pages}:")
for pt in pts:
    p = pt.payload or {}
    if p.get("page") in target_pages:
        content = p.get("content", "")
        meta = p.get("metadata", {}) or {}
        print(f"\n  Page {p.get('page')} | path: {meta.get('image_path', '')[-40:]}")
        print(f"  Content: {content[:200]!r}")
