from agents.chat_agent import run_chat_agent
from core.state import AgentState
import pandas as pd

def test_chat_after_pipeline():

    df = pd.DataFrame({
        "sales": [100, 200, 300]
    })

    state = AgentState()
    state.dataset = df
    state.cleaned_data = df

    response = run_chat_agent("total sales", state)

    assert response is not None