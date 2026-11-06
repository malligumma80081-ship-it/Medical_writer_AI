from app.embeddings.embedding_model import get_embedding_model


class EmbeddingService:

    def __init__(self):
        self.model = get_embedding_model()

    def generate_embedding(self, text: str) -> list[float]:
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text")

        vector = self.model.encode(
            text,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        return vector.tolist()

    def generate_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        if not texts:
            return []

        if any(not text.strip() for text in texts):
            raise ValueError("Input contains empty text")

        vectors = self.model.encode(
            texts,
            batch_size=32,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        return vectors.tolist()