from app.agents.state import AgentState
from app.rag.retriever import retriever

async def retriever_node(state: AgentState) -> AgentState:
    # Bug: document_ids from state is not passed to retriever
    docs = retriever.retrieve(
        question=state["question"],
        org_id=state["org_id"],
    )
    return {**state, "retrieved_docs": docs, "steps": [f"Retrieved {len(docs)} chunks"]}
