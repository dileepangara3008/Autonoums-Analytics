from core.config import get_llm
import json
from langsmith import traceable

@traceable(name="Insights Agent")
def run_insights_agent(df, eda_results, stats_results):

    llm = get_llm()

    # -----------------------------
    # 🧠 PROMPT (GENERALIZED)
    # -----------------------------
    prompt = f"""
    You are a senior data analyst.

    Your task is to generate HIGH-QUALITY, DATA-DRIVEN insights.

    You are given:
    - Dataset sample
    - EDA results
    - Statistical analysis results

    --------------------------------------------------

    DATASET SAMPLE:
    {df.head().to_json()}

    EDA RESULTS:
    {eda_results}

    STATISTICAL RESULTS:
    {stats_results}

    --------------------------------------------------

    OBJECTIVE:
    Generate insights that are:
    - Accurate (based ONLY on given data)
    - Non-obvious (avoid trivial statements)
    - Actionable (useful for decision making)

    --------------------------------------------------

    STRICT RULES:

    - Use ONLY the provided data and results
    - DO NOT hallucinate or assume patterns
    - DO NOT repeat raw numbers unless needed
    - DO NOT restate obvious facts (e.g., "data has multiple columns")
    - Each insight must be meaningful and distinct

    --------------------------------------------------

    INSIGHT STRATEGY:

    1. KEY INSIGHTS
      - Focus on strongest patterns from EDA
      - Highlight important distributions or trends

    2. RELATIONSHIPS
      - MUST use statistical results (correlation/regression)
      - Mention strength (strong/weak) and direction (positive/negative)

    3. ANOMALIES
      - Use anomaly detection or distribution skew
      - Highlight unusual patterns or outliers

    4. RECOMMENDATIONS
      - MUST be based on insights (not generic advice)
      - Should be actionable and specific

    --------------------------------------------------

    QUALITY CHECK (VERY IMPORTANT):

    Before finalizing:
    - Remove generic insights
    - Remove repeated ideas
    - Ensure each point adds new value

    --------------------------------------------------

    OUTPUT FORMAT (STRICT JSON ONLY):

    {{
      "key_insights": [
        "..."
      ],
      "relationships": [
        "..."
      ],
      "anomalies": [
        "..."
      ],
      "recommendations": [
        "..."
      ]
    }}

    DO NOT include any text outside JSON.
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