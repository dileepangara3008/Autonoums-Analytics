from agents.ingestion_agent import ingestion_agent
from core.state import AgentState
import io


def test_hitl_after_ingestion():

    csv = "a,b\n1,2"
    file = io.StringIO(csv)

    state = AgentState()
    state.file = file

    state = ingestion_agent(state)

    assert state.waiting_for_input is True
    assert state.current_stage == "CLEANING"
