from core.config import get_llm
import json
import re
from langsmith import traceable


# -----------------------------
# 🔥 JSON EXTRACTOR
# -----------------------------
def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    return text


# -----------------------------
# 🔥 NORMALIZE KEYS
# -----------------------------
def normalize_keys(insights):
    return {
        "key_insights": insights.get("key_insights") or insights.get("Key Insights") or [],
        "relationships": insights.get("relationships") or insights.get("Relationships") or [],
        "anomalies": insights.get("anomalies") or insights.get("Anomalies") or [],
        "recommendations": insights.get("recommendations") or insights.get("Recommendations") or []
    }


# -----------------------------
# 🔥 CLEAN OUTPUT
# -----------------------------
def clean_insights(insights):

    def clean_list(items):
        return [
            i.strip()
            for i in items
            if isinstance(i, str) and len(i.strip()) > 10
        ][:4]  # limit size

    return {
        "key_insights": clean_list(insights.get("key_insights", [])),
        "relationships": clean_list(insights.get("relationships", [])),
        "anomalies": clean_list(insights.get("anomalies", [])),
        "recommendations": clean_list(insights.get("recommendations", []))
    }


# -----------------------------
# 🧠 INSIGHTS AGENT
# -----------------------------
@traceable(name="Insights Agent")
def run_insights_agent(df, eda_results, stats_results):

    llm = get_llm()

    prompt = f"""
    You are a senior data analyst.

    Your job is to generate HIGH-QUALITY, DATA-GROUNDED insights.

    --------------------------------------------------

    DATASET SAMPLE:
    {df.head().to_json()}

    EDA RESULTS:
    {eda_results}

    STATISTICAL RESULTS:
    {stats_results}

    --------------------------------------------------

    CRITICAL RULES:

    - Use ONLY the provided data
    - DO NOT hallucinate numbers or relationships
    - DO NOT give generic advice
    - Keep insights concise and meaningful

    --------------------------------------------------

    STRUCTURE:

    1. KEY INSIGHTS (max 3-4)
    2. RELATIONSHIPS (only strong ones from stats)
    3. ANOMALIES (based on skew/outliers)
    4. RECOMMENDATIONS (must follow insights)

    --------------------------------------------------

    OUTPUT STRICT JSON ONLY:

    {{
      "key_insights": [],
      "relationships": [],
      "anomalies": [],
      "recommendations": []
    }}
    """

    response = llm.invoke(prompt).content.strip()

    # -----------------------------
    # 🛡️ ROBUST PARSE
    # -----------------------------
    try:
        cleaned = extract_json(response)
        insights = json.loads(cleaned)
    except:
        insights = {
            "key_insights": [response],
            "relationships": [],
            "anomalies": [],
            "recommendations": []
        }

    # -----------------------------
    # 🔥 NORMALIZE + CLEAN
    # -----------------------------
    insights = normalize_keys(insights)
    insights = clean_insights(insights)

    return insights