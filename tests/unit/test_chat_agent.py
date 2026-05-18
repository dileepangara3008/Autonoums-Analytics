from agents.chat_agent import run_chat_agent


def test_chat_runs(sample_state):

    response = run_chat_agent("total sales", sample_state)

    assert response is not None

def test_chat_unknown_query(sample_state):

    response = run_chat_agent("tell me a joke", sample_state)

    assert response is not None