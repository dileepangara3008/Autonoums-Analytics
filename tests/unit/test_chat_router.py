from agents.chat_agent import detect_query_type


def test_data_query():
    assert detect_query_type("total sales") == "data"


def test_viz_query():
    assert detect_query_type("plot sales") == "viz"


def test_insight_query():
    assert detect_query_type("why sales high") == "insight"