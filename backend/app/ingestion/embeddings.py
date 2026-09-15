from sentence_transformers import SentenceTransformer

from app.config.settings import settings

_MODEL_CACHE: dict[str, SentenceTransformer] = {}


class EmbeddingService:
    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or settings.embedding_model

        if not self.model_name:
            raise ValueError("EMBEDDING_MODEL is not configured")

        if self.model_name not in _MODEL_CACHE:
            _MODEL_CACHE[self.model_name] = SentenceTransformer(self.model_name)
        
        self.model = _MODEL_CACHE[self.model_name]

    def embed(self, text: str) -> list[float]:
        vector = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return vector.tolist()

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(
            texts,
            normalize_embeddings=True,
        )

        return vectors.tolist()
