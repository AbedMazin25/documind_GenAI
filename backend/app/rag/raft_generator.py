from openai import AsyncOpenAI
from app.config import settings
import json, uuid

_client = AsyncOpenAI(api_key=settings.openai_api_key)

QA_PROMPT = (
    "You are generating synthetic training data for a financial QA model (RAFT). "
    "Given the context, generate {n} question-answer pairs where the answer is grounded in the context. "
    "Also generate {n} distractor documents that are plausible but wrong. "
    "Return JSON: {\"samples\": [{\"question\": str, \"answer\": str, \"cot\": str}], "
    "\"distractors\": [str]}"
)

class RAFTGenerator:
    async def generate(self, context: str, n: int = 3) -> list[dict]:
        resp = await _client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": QA_PROMPT.format(n=n)},
                {"role": "user", "content": context[:6000]},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        try:
            data = json.loads(resp.choices[0].message.content)
        except (json.JSONDecodeError, KeyError):
            return []
        samples = data.get("samples", [])
        distractors = data.get("distractors", [])
        raft_samples = []
        for s in samples:
            raft_samples.append({
                "id": str(uuid.uuid4()),
                "question": s["question"],
                "oracle_context": context,
                "cot_answer": s.get("cot", ""),
                "answer": s["answer"],
                "distractors": distractors,
                "type": "raft",
            })
        return raft_samples

    async def generate_dataset(self, chunks: list[str], samples_per_chunk: int = 2) -> list[dict]:
        all_samples = []
        for chunk in chunks:
            if len(chunk.split()) < 50:
                continue
            samples = await self.generate(chunk, n=samples_per_chunk)
            all_samples.extend(samples)
        return all_samples

raft_gen = RAFTGenerator()
