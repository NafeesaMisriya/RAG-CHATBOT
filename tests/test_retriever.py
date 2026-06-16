from app.retrieval.retriever import (
    Retriever
)

retriever = Retriever()

results = retriever.retrieve(
    query=
    "Explain the structure of DNA",

    collection_name=
    "documents",

    limit=5
)

print("\nTOP RESULTS:\n")

for result in results:

    print(
        f"Score: "
        f"{result['score']:.4f}"
    )

    print(
        f"Page: "
        f"{result['page']}"
    )

    print(
        "\nContent:"
    )

    print(
        result["content"]
    )

    print(
        "\n" + "=" * 80
    )