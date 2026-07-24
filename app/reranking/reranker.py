import os

class Reranker:

    def __init__(self):
        self.enabled = os.environ.get("RERANK_ENABLED", "true").lower() == "true"
        if self.enabled:
            # Lazy import to prevent loading heavy torch/transformers into memory in cloud
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(
                "cross-encoder/ms-marco-MiniLM-L-12-v2"
            )

    def rerank(
        self,
        query,
        contexts,
        top_k=15
    ):

        if not contexts:

            return []

        if not self.enabled:
            # Return original contexts sorted by their retriever hybrid_score/score
            contexts_sorted = sorted(
                contexts,
                key=lambda x: x.get("hybrid_score", x.get("score", 0)),
                reverse=True
            )
            return contexts_sorted[:top_k]

        pairs = [

            (
                query,
                context["content"]
            )

            for context in contexts
        ]

        scores = (
            self.model.predict(
                pairs
            )
        )

        ranked = []

        for context, score in zip(
            contexts,
            scores
        ):

            context[
                "rerank_score"
            ] = float(score)

            ranked.append(
                context
            )

        ranked.sort(
            key=lambda x:
            x["rerank_score"],
            reverse=True
        )

        print(
            "\n===== RERANK RESULTS ====="
        )

        for item in ranked[:10]:

            print(
                f"Page "
                f"{item['page']} | "
                f"Hybrid "
                f"{item.get('hybrid_score',0):.4f} | "
                f"Rerank "
                f"{item['rerank_score']:.4f} | "
                f"Type "
                f"{item.get('node_type')}"
            )

        return ranked[:top_k]