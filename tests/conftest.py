import pytest
import pandas as pd
from core.state import AgentState
import warnings

warnings.filterwarnings("ignore")

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "region": ["East", "West", "North"],
        "sales": [100, 200, 150],
        "price": [10, 20, 15]
    })


@pytest.fixture
def sample_state(sample_df):
    state = AgentState()
    state.dataset = sample_df
    return state