from openai import AsyncOpenAI
from app.agents.state import AgentState
from app.config import settings
import json

_client = AsyncOpenAI(api_key=settings.openai_api_key)

ROUTE_PROMPT = (
    "Classify the financial question into one of: rag, analytical, direct.\n"
    "- rag: requires document retrieval (earnings, filings, transcripts)\n"
    "- analytical: requires computation (ratios, DCF, comparisons)\n"
    "- direct: general knowledge, no retrieval needed\n"
    "Respond with JSON: {\"route\": \"<category>\"}"
)

async def router_node(state: AgentState) -> AgentState:
    resp = await _client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": ROUTE_PROMPT},
            {"role": "user", "content": state["question"]},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    data = json.loads(resp.choices[0].message.content)
    route = data.get("route", "rag")
    return {**state, "route": route, "steps": [f"Routed to: {route}"]}
