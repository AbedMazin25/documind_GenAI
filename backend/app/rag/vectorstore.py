import chromadb
from app.config import settings

class VectorStore:
    def __init__(self):
        self.client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
        )

    def get_or_create_collection(self, name: str):
        return self.client.get_or_create_collection(name)

    def query_collection(self, name: str, query_embedding: list[float], k: int = 6, where: dict = None):
        collection = self.get_or_create_collection(name)
        kwargs = {"query_embeddings": [query_embedding], "n_results": k, "include": ["documents", "metadatas", "distances"]}
        if where:
            kwargs["where"] = where
        return collection.query(**kwargs)

    def delete_collection(self, name: str):
        try:
            self.client.delete_collection(name)
        except Exception:
            pass
