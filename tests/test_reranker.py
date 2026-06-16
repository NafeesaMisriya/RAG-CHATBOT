# tests/test_reranker.py

from app.retrieval.retriever import (
    Retriever
)

from app.reranking.reranker import (
    Reranker
)

query = (
    "What is DNA?"
)

retriever = Retriever()

contexts = retriever.retrieve(
    query=query,
    collection_name="documents",
    limit=15
)

print("\n" + "=" * 80)
print("RETRIEVED CHUNKS")
print("=" * 80)

for i, context in enumerate(
    contexts,
    start=1
):

    print(
        f"\nChunk {i}"
    )

    print(
        f"Page: "
        f"{context['page']}"
    )

    print(
        f"Retrieval Score: "
        f"{context['score']}"
    )

    print(
        context["content"][:300]
    )

    print(
        "\n" + "-" * 80
    )

reranker = Reranker()

top_contexts = reranker.rerank(
    query=query,
    contexts=contexts,
    top_k=3
)

print("\n" + "=" * 80)
print("AFTER RERANKING")
print("=" * 80)

for i, context in enumerate(
    top_contexts,
    start=1
):

    print(
        f"\nTop {i}"
    )

    print(
        f"Page: "
        f"{context['page']}"
    )

    print(
        f"Rerank Score: "
        f"{context['rerank_score']:.4f}"
    )

    print(
        context["content"][:500]
    )

    print(
        "\n" + "=" * 80
    )
    