from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes.router import router_node
from app.agents.nodes.retriever import retriever_node
from app.agents.nodes.analyzer import analyzer_node
from app.agents.nodes.responder import responder_node

def route_decision(state: AgentState) -> str:
    return state.get("route", "rag")

def build_graph():
    g = StateGraph(AgentState)
    g.add_node("router", router_node)
    g.add_node("retriever", retriever_node)
    g.add_node("analyzer", analyzer_node)
    g.add_node("responder", responder_node)

    g.set_entry_point("router")
    g.add_conditional_edges(
        "router",
        route_decision,
        {
            "rag": "retriever",
            "analytical": "retriever",
            "direct": "responder",
        },
    )
    g.add_edge("retriever", "analyzer")
    g.add_edge("analyzer", "responder")
    g.add_edge("responder", END)
    return g.compile()

agent_graph = build_graph()
