from openai import AsyncOpenAI
from app.config import settings

_client = AsyncOpenAI(api_key=settings.openai_api_key)

RERANK_PROMPT = (
    "Score the relevance of each document passage to the query on a scale 0-10. "
    "Return JSON: {\"scores\": [float, ...]}"
)

class ColBERTReranker:
    async def rerank(self, question: str, docs: list[dict], top_k: int = 4) -> list[dict]:
        if not docs:
            return docs
        passages = [d["text"][:500] for d in docs]
        prompt = f"Query: {question}\n\nPassages:\n" + "\n".join(f"{i+1}. {p}" for i, p in enumerate(passages))
        resp = await _client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": RERANK_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        try:
            import json
            scores = json.loads(resp.choices[0].message.content).get("scores", [])
        except Exception:
            scores = [1.0] * len(docs)
        scored = list(zip(docs, scores))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [d for d, _ in scored[:top_k]]

reranker = ColBERTReranker()
