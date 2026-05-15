from langgraph.graph import StateGraph
from core.state import AgentState
from graph.nodes import nodes


def build_graph():

    graph = StateGraph(AgentState)

    # -----------------------------
    # ➕ Add Nodes
    # -----------------------------
    for name, node in nodes.items():
        graph.add_node(name, node)

    # -----------------------------
    # 🎯 ENTRY POINT
    # -----------------------------
    graph.set_entry_point("INGESTION")

    # -----------------------------
    # 🔗 SEQUENTIAL FLOW
    # -----------------------------

    graph.add_edge("INGESTION", "EDA")
    graph.add_edge("EDA", "STATS")
    graph.add_edge("STATS", "VIZ")
    graph.add_edge("VIZ", "INSIGHTS")
    graph.add_edge("INSIGHTS", "__end__")

    return graph.compile()