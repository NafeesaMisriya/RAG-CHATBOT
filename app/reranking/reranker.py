from sentence_transformers import (
    CrossEncoder
)


class Reranker:

    def __init__(self):

        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-12-v2"
        )

    def rerank(
        self,
        query,
        contexts,
        top_k=3,
        min_score=-10.0
    ):

        if not contexts:
            return []

        pairs = [
            (
                query,
                context["content"]
            )
            for context in contexts
        ]

        scores = self.model.predict(
            pairs
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
            "\nTop Rerank Scores:"
        )

        for item in ranked[:10]:

            print(
                f"Page: "
                f"{item['page']} | "
                f"Score: "
                f"{item['rerank_score']:.4f}"
            )

    

        return ranked[:top_k]