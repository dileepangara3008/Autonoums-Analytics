from langgraph.graph import StateGraph
from core.state import AgentState
from graph.supervisor import supervisor

def build_graph(nodes):
    
    graph = StateGraph(AgentState)
    
    for name, node in nodes.items():
        graph.add_node(name, node)
    
    graph.set_entry_point("SUPERVISOR")
    
    graph.add_conditional_edges(
        "SUPERVISOR",
        supervisor,
        {
            "HITL": "HITL_NODE",
            "EDA_AGENT": "EDA_AGENT",
            "END": "__end__"
        }
    )
    
    return graph.compile()