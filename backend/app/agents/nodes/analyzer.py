from openai import AsyncOpenAI
from app.agents.state import AgentState
from app.config import settings

_client = AsyncOpenAI(api_key=settings.openai_api_key)

ANALYST_PROMPT = (
    "You are a financial analyst. Given the retrieved context and the question, "
    "perform any necessary calculations, ratio analysis, or trend identification. "
    "Show your reasoning step by step."
)

async def analyzer_node(state: AgentState) -> AgentState:
    context = "\n\n".join(d["text"] for d in state.get("retrieved_docs", []))
    resp = await _client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": ANALYST_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {state['question']}"},
        ],
        temperature=0.1,
    )
    analysis = resp.choices[0].message.content
    return {**state, "analysis": analysis, "steps": ["Ran financial analysis"]}
