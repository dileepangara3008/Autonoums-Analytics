from core.config import get_llm
import json


def run_insights_agent(df, eda_results, stats_results):

    llm = get_llm()

    # -----------------------------
    # 🧠 PROMPT (GENERALIZED)
    # -----------------------------
    prompt = f"""
    You are a senior data analyst.

    You are given:
    - dataset sample
    - EDA results
    - statistical analysis results

    Your task:
    Generate clear, meaningful insights.

    Dataset sample:
    {df.head().to_json()}

    EDA Results:
    {eda_results}

    Statistical Results:
    {stats_results}

    Guidelines:
    - Focus on patterns, relationships, and anomalies
    - Avoid repeating raw numbers unless necessary
    - Provide business-relevant insights (not technical explanation)
    - Be concise and actionable

    Return STRICT JSON in this format:

    {{
      "key_insights": [
        "insight 1",
        "insight 2",
        "insight 3"
      ],
      "relationships": [
        "relationship 1",
        "relationship 2"
      ],
      "anomalies": [
        "anomaly 1"
      ],
      "recommendations": [
        "recommendation 1",
        "recommendation 2"
      ]
    }}
    """

    response = llm.invoke(prompt).content.strip()

    # -----------------------------
    # 🛡️ SAFE PARSE
    # -----------------------------
    try:
        insights = json.loads(response)
    except:
        insights = {
            "key_insights": [response],
            "relationships": [],
            "anomalies": [],
            "recommendations": []
        }

    return insights