from app.agents.graph import agent_graph
from app.agents.state import AgentState
from typing import Optional

class AgentService:
    async def run(self, question: str, org_id: str, document_ids: Optional[list[str]] = None) -> dict:
        initial: AgentState = {
            "question": question,
            "org_id": org_id,
            "document_ids": document_ids,
            "route": None,
            "retrieved_docs": [],
            "analysis": None,
            "answer": None,
            "steps": [],
        }
        result = await agent_graph.ainvoke(initial)
        return {
            "answer": result.get("answer", ""),
            "sources": [d["metadata"] for d in result.get("retrieved_docs", [])],
            "steps": result.get("steps", []),
        }
