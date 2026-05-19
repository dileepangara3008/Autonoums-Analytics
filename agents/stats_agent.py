from core.config import get_llm
from tools.stats_tools import (
    correlation_test_tool,
    t_test_tool,
    regression_tool,
    anomaly_detection_tool,
    distribution_tool
)
import json
from langsmith import traceable

# -----------------------------
# 🔐 SAFE COLUMN VALIDATION
# -----------------------------
def safe_column(col, df):
    return col if col in df.columns else None

@traceable(name="Stats Agent")
def run_stats_agent(df, eda_results=None):

    llm = get_llm()
    data_json = df.to_json()

    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    # -----------------------------
    # 🧠 LLM DECIDES TOOLS + COLUMNS
    # -----------------------------
    prompt = f"""
    You are a data analyst.

    You are given a dataset schema and a sample.

    Your task:
    1. Decide which statistical analyses are relevant
    2. Select appropriate columns for each analysis

    Dataset columns:
    {df.columns.tolist()}

    Numeric columns:
    {df.select_dtypes(include="number").columns.tolist()}

    Sample data:
    {df.head().to_json()}

    Available tools:
    - correlation (requires 2 numeric columns)
    - regression (requires 2 numeric columns)
    - anomaly_detection (requires 1 numeric column)
    - distribution (requires 1 numeric column)
    - t_test (requires 2 numeric columns)

    Guidelines:
    - Use only numeric columns for statistical tests
    - Avoid columns that look like identifiers (e.g., IDs, indexes)
    - Prefer columns that represent measurable quantities
    - Choose meaningful relationships between variables
    - Do not repeat the same analysis unnecessarily

    Return STRICT JSON list like:

    [
    {{
        "tool": "correlation",
        "col1": "column_a",
        "col2": "column_b"
    }},
    {{
        "tool": "distribution",
        "column": "column_c"
    }}
    ]

    Do not return anything other than valid JSON.
    """

    decision = llm.invoke(prompt).content.strip()

    try:
        plan = json.loads(decision)
    except:
        plan = []

    results = {}

    # -----------------------------
    # ⚙️ EXECUTE PLAN
    # -----------------------------
    for item in plan:

        tool_name = item.get("tool")

        try:

            # -----------------------------
            # 📊 CORRELATION
            # -----------------------------
            if tool_name == "correlation":

                col1 = safe_column(item.get("col1"), df)
                col2 = safe_column(item.get("col2"), df)

                if col1 and col2:
                    results["correlation"] = correlation_test_tool.invoke({
                        "input_json": json.dumps({
                            "data": data_json,
                            "col1": col1,
                            "col2": col2
                        })
                    })

            # -----------------------------
            # 📈 REGRESSION
            # -----------------------------
            elif tool_name == "regression":

                col1 = safe_column(item.get("col1"), df)
                col2 = safe_column(item.get("col2"), df)

                if col1 and col2:
                    results["regression"] = regression_tool.invoke({
                        "input_json": json.dumps({
                            "data": data_json,
                            "feature": col1,
                            "target": col2
                        })
                    })

            # -----------------------------
            # 🚨 ANOMALY
            # -----------------------------
            elif tool_name == "anomaly_detection":

                column = safe_column(item.get("column"), df)

                if column:
                    results["anomaly"] = anomaly_detection_tool.invoke({
                        "input_json": json.dumps({
                            "data": data_json,
                            "column": column
                        })
                    })

            # -----------------------------
            # 📊 DISTRIBUTION
            # -----------------------------
            elif tool_name == "distribution":

                column = safe_column(item.get("column"), df)

                if column:
                    results["distribution"] = distribution_tool.invoke({
                        "input_json": json.dumps({
                            "data": data_json,
                            "column": column
                        })
                    })

            # -----------------------------
            # 🧪 T-TEST
            # -----------------------------
            elif tool_name == "t_test":

                col1 = safe_column(item.get("col1"), df)
                col2 = safe_column(item.get("col2"), df)

                if col1 and col2:
                    results["t_test"] = t_test_tool.invoke({
                        "input_json": json.dumps({
                            "data": data_json,
                            "col1": col1,
                            "col2": col2
                        })
                    })

        except Exception as e:
            results[tool_name] = f"Error: {str(e)}"

    # -----------------------------
    # 🧠 FINAL SUMMARY
    # -----------------------------
    summary_prompt = f"""
    You are a business analyst.

    Based on statistical results:

    {results}

    Generate:
    - 3 key insights
    - 2 relationships between variables
    - 1 anomaly (if any)

    Keep it simple and business-focused.
    Avoid technical jargon.
    """

    summary = llm.invoke(summary_prompt).content

    return {
        "plan": plan,
        "results": results,
        "summary": summary
    }