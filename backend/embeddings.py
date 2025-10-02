from typing import List
from sentence_transformers import SentenceTransformer

# Загружаем модель один раз при старте
# можно заменить на любую другую (например, "all-MiniLM-L6-v2" или ru-модель)
_embedder = SentenceTransformer("distiluse-base-multilingual-cased-v1")

async def embed_text(text: str) -> List[float]:
    """Генерация векторного представления текста отзыва."""
    embedding = _embedder.encode([text])[0]  # берём первый (и единственный) элемент
    return embedding.tolist()