from openai import AsyncOpenAI
from app.agents.state import AgentState
from app.config import settings

_client = AsyncOpenAI(api_key=settings.openai_api_key)

RESPONDER_PROMPT = (
    "You are DocuMind. Synthesize the retrieved context and analysis into a clear, "
    "cited response. Reference specific documents and figures where possible."
)

async def responder_node(state: AgentState) -> AgentState:
    context = "\n\n".join(d["text"] for d in state.get("retrieved_docs", []))
    analysis = state.get("analysis", "")
    user_content = f"Context:\n{context}\n\nAnalysis:\n{analysis}\n\nQuestion: {state['question']}"
    resp = await _client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": RESPONDER_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
    )
    answer = resp.choices[0].message.content
    return {**state, "answer": answer, "steps": ["Generated final response"]}
