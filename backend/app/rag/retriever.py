from app.rag.vectorstore import VectorStore
from app.services.embedding_service import embed_query
from app.config import settings

vector_store = VectorStore()

class DenseRetriever:
    def retrieve(
        self,
        question: str,
        org_id: str,
        k: int = None,
        document_ids: list[str] = None,
    ) -> list[dict]:
        k = k or settings.retrieval_k
        query_vec = embed_query(question)
        where = {}
        if document_ids:
            where["doc_id"] = {"$in": document_ids}
        results = vector_store.query_collection(org_id, query_vec, k=k, where=where or None)
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        return [
            {"text": doc, "metadata": meta, "score": 1 - dist}
            for doc, meta, dist in zip(docs, metas, distances)
        ]

retriever = DenseRetriever()
