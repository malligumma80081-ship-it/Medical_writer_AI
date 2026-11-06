from functools import lru_cache

from sentence_transformers import CrossEncoder


RERANKER_MODEL = "BAAI/bge-reranker-base"


@lru_cache(maxsize=1)
def get_reranker():
    return CrossEncoder(RERANKER_MODEL)


class MedicalReranker:

    def __init__(self):
        self.model = get_reranker()

    def rerank(
        self,
        query: str,
        evidence: list[dict],
        top_k: int = 5,
    ) -> list[dict]:

        if not evidence:
            return []

        pairs = [
            (query, item["content"])
            for item in evidence
        ]

        scores = self.model.predict(
            pairs,
            show_progress_bar=False,
        )

        ranked = []

        for item, score in zip(evidence, scores):
            result = item.copy()
            result["rerank_score"] = float(score)
            ranked.append(result)

        ranked.sort(
            key=lambda item: item["rerank_score"],
            reverse=True,
        )

        return ranked[:top_k]