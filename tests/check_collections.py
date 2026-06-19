"""Quick diagnostic: show all collections with point counts and image node counts."""
import sys
sys.path.insert(0, ".")

from app.retrieval.qdrant_manager import QdrantManager
from qdrant_client.models import Filter, FieldCondition, MatchValue

qm = QdrantManager()

collections = qm.list_collections().collections
print(f"\n{'Collection':<20} {'Total':>8} {'Images':>8} {'Text':>8}")
print("-" * 50)

for col in collections:
    name = col.name
    try:
        total = qm.count_points(name)

        # Count image nodes
        image_count = qm.client.count(
            collection_name=name,
            count_filter=Filter(
                must=[FieldCondition(key="metadata.node_type", match=MatchValue(value="image"))]
            ),
            exact=True
        ).count

        text_count = total - image_count
        print(f"{name:<20} {total:>8} {image_count:>8} {text_count:>8}")

        # Sample 1 image node to check if figure-context enrichment is present
        if image_count > 0:
            pts, _ = qm.client.scroll(
                collection_name=name,
                scroll_filter=Filter(
                    must=[FieldCondition(key="metadata.node_type", match=MatchValue(value="image"))]
                ),
                limit=1,
                with_payload=True,
                with_vectors=False
            )
            if pts:
                content = pts[0].payload.get("content", "")
                has_figure_ctx = content.startswith("FIGURE:")
                print(f"  └─ figure-context enrichment: {'YES' if has_figure_ctx else 'NO'}")
                print(f"  └─ sample content: {content[:120]!r}")

    except Exception as e:
        print(f"{name:<20} ERROR: {e}")

print()
