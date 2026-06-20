from rank_bm25 import BM25Okapi
from app.rag.vectorstore import VectorStore
from app.services.embedding_service import embed_query
from app.config import settings

def _rrf(rank_lists: list[list[int]], k: int = 60) -> list[float]:
    scores = {}
    for ranks in rank_lists:
        for rank, doc_idx in enumerate(ranks):
            scores[doc_idx] = scores.get(doc_idx, 0) + 1.0 / (k + rank + 1)
    return scores

class HybridRetriever:
    def __init__(self):
        self._vector_store = None

    @property
    def vector_store(self) -> VectorStore:
        if self._vector_store is None:
            self._vector_store = VectorStore()
        return self._vector_store

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
        dense_res = self.vector_store.query_collection(org_id, query_vec, k=k * 2, where=where or None)
        dense_docs = dense_res.get("documents", [[]])[0]
        dense_metas = dense_res.get("metadatas", [[]])[0]
        dense_distances = dense_res.get("distances", [[]])[0]
        if not dense_docs:
            return []
        tokenized = [d.lower().split() for d in dense_docs]
        bm25 = BM25Okapi(tokenized)
        bm25_scores = bm25.get_scores(question.lower().split())
        bm25_rank = sorted(range(len(bm25_scores)), key=lambda i: -bm25_scores[i])
        dense_rank = list(range(len(dense_docs)))
        rrf_scores = _rrf([dense_rank, bm25_rank])
        top_indices = sorted(rrf_scores, key=lambda i: -rrf_scores[i])[:k]
        return [
            {
                "text": dense_docs[i],
                "metadata": dense_metas[i],
                "score": rrf_scores[i],
                "bm25_score": float(bm25_scores[i]),
            }
            for i in top_indices
        ]

retriever = HybridRetriever()
