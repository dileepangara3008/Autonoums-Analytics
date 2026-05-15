from core.config import get_llm

def route_query(query):

    llm = get_llm()

    prompt = f"""
    Decide which agent to use.

    Options:
    EDA
    STATS
    VIZ
    INSIGHTS

    Query:
    {query}

    Return ONLY one word.
    """

    decision = llm.invoke(prompt).content.strip().upper()

    return decision