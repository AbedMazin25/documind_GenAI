from app.agents.graph import agent_graph
from app.agents.state import AgentState
from typing import Optional, AsyncGenerator

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

    def _initial_state(self, question, org_id, document_ids) -> AgentState:
        return {
            "question": question,
            "org_id": org_id,
            "document_ids": document_ids,
            "route": None,
            "retrieved_docs": [],
            "analysis": None,
            "answer": None,
            "steps": [],
        }

    async def stream(
        self,
        question: str,
        org_id: str,
        document_ids: Optional[list[str]] = None,
    ) -> AsyncGenerator[str, None]:
        async for event in agent_graph.astream(
            self._initial_state(question, org_id, document_ids)
        ):
            for node, state in event.items():
                if node == "responder" and state.get("answer"):
                    yield state["answer"]

    async def stream_events(
        self,
        question: str,
        org_id: str,
        document_ids: Optional[list[str]] = None,
    ) -> AsyncGenerator[dict, None]:
        """Yields structured events: {'type': 'status', 'content': ...} for
        intermediate reasoning steps, and {'type': 'token', 'content': ...} for
        the user-facing answer."""
        async for event in agent_graph.astream(
            self._initial_state(question, org_id, document_ids)
        ):
            for node, state in event.items():
                if node == "responder" and state.get("answer"):
                    yield {"type": "token", "content": state["answer"]}
                elif "steps" in state and state["steps"]:
                    yield {"type": "status", "content": state["steps"][-1]}
