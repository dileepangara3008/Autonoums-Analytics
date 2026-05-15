from langchain.tools import tool
from core.config import get_llm

@tool
def insights_tool(data: str, eda: str, stats: str) -> str:
    """
    Generate insights from dataset and analysis results.
    """

    llm = get_llm()

    prompt = f"""
    Analyze the following dataset and results:

    DATA:
    {data[:1000]}

    EDA:
    {eda}

    STATS:
    {stats}

    Generate:
    - Key insights
    - Trends
    - Anomalies
    - Recommendations
    """

    return llm.invoke(prompt).content