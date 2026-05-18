from graph.builder import build_graph
from core.state import AgentState
import pandas as pd


def test_full_pipeline():

    graph = build_graph()

    df = pd.DataFrame({
        "region": ["East", "West"],
        "sales": [100, 200],
        "price": [10, 20]
    })

    state = AgentState()
    state.dataset = df
    state.cleaned_data = df   # skip HITL for test

    result = graph.invoke(state)

    assert result is not None