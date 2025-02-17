from openai import OpenAI
from app.config import settings

_client = OpenAI(api_key=settings.openai_api_key)

def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    batch_size = settings.embed_batch_size if hasattr(settings, "embed_batch_size") else 64
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        resp = _client.embeddings.create(model=settings.embedding_model, input=batch)
        embeddings.extend([item.embedding for item in resp.data])
    return embeddings

def embed_query(text: str) -> list[float]:
    resp = _client.embeddings.create(model=settings.embedding_model, input=[text])
    return resp.data[0].embedding
