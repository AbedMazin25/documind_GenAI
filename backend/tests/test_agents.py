import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from app.agents.state import AgentState

def make_state(**kwargs) -> AgentState:
    defaults = {
        "question": "What was revenue in Q3?",
        "org_id": "test-org",
        "document_ids": None,
        "route": None,
        "retrieved_docs": [],
        "analysis": None,
        "answer": None,
        "steps": [],
    }
    return {**defaults, **kwargs}

@pytest.mark.asyncio
async def test_router_classifies_financial():
    with patch("app.agents.nodes.router._client") as mock_client:
        mock_client.chat.completions.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content='{"route": "analytical"}'))]
        ))
        from app.agents.nodes.router import router_node
        state = await router_node(make_state(question="Calculate PE ratio for Apple"))
        assert state["route"] == "analytical"

@pytest.mark.asyncio
async def test_retriever_passes_document_ids():
    with patch("app.agents.nodes.retriever.retriever") as mock_retriever:
        mock_retriever.retrieve = MagicMock(return_value=[{"text": "Revenue was $100M", "metadata": {}}])
        from app.agents.nodes.retriever import retriever_node
        state = await retriever_node(make_state(document_ids=["doc-123"]))
        mock_retriever.retrieve.assert_called_once()
        call_kwargs = mock_retriever.retrieve.call_args[1]
        assert call_kwargs.get("document_ids") == ["doc-123"]
        assert len(state["retrieved_docs"]) == 1

@pytest.mark.asyncio
async def test_agent_graph_routes_direct_query():
    from app.agents.graph import route_decision
    state = make_state(route="direct")
    assert route_decision(state) == "direct"

@pytest.mark.asyncio
async def test_agent_graph_routes_rag_to_retriever():
    from app.agents.graph import route_decision
    state = make_state(route="rag")
    assert route_decision(state) == "rag"
