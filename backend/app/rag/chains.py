from openai import AsyncOpenAI
from app.rag.retriever import retriever
from app.config import settings

_client = AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = (
    "You are DocuMind, a financial analyst assistant. "
    "Answer the user's question using ONLY the provided context. "
    "If you cannot answer from the context, say so. "
    "Always cite the source document."
)

class RAGChain:
    async def run(self, question: str, org_id: str, document_ids=None, k: int = 6) -> dict:
        docs = retriever.retrieve(question, org_id, k=k, document_ids=document_ids)
        context = "\n\n---\n\n".join(d["text"] for d in docs)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ]
        resp = await _client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0.1,
        )
        return {
            "answer": resp.choices[0].message.content,
            "sources": [d["metadata"] for d in docs],
        }

rag_chain = RAGChain()
