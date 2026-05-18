import io
from agents.ingestion_agent import ingestion_agent
from core.state import AgentState


def test_ingestion():

    csv = "region,sales\nEast,100\nWest,200"
    file = io.StringIO(csv)

    state = AgentState()
    state.file = file

    result = ingestion_agent(state)

    assert result.dataset is not None
    assert not result.dataset.empty


def test_ingestion_invalid_file():

    file = io.StringIO("not,a,valid,csv,,,")
    
    state = AgentState()
    state.file = file

    result = ingestion_agent(state)

    # either dataset exists OR error captured
    assert result.dataset is not None or result.errors

def test_ingestion_sets_flags():

    import io
    from agents.ingestion_agent import ingestion_agent
    from core.state import AgentState

    csv = "a,b\n1,2"
    file = io.StringIO(csv)

    state = AgentState()
    state.file = file

    result = ingestion_agent(state)

    assert result.current_stage == "CLEANING"
    assert result.waiting_for_input is True