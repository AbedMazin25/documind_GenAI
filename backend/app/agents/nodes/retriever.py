from app.agents.state import AgentState
from app.rag.retriever import retriever

async def retriever_node(state: AgentState) -> AgentState:
    docs = retriever.retrieve(
        question=state["question"],
        org_id=state["org_id"],
        document_ids=state.get("document_ids"),
    )
    return {**state, "retrieved_docs": docs, "steps": [f"Retrieved {len(docs)} chunks"]}
