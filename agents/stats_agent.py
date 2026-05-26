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
from core.logger import logger


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
    # 🧠 LLM DECIDES PLAN
    # -----------------------------
    prompt = f"""
    You are a data analyst.

    Dataset columns:
    {df.columns.tolist()}

    Numeric columns:
    {numeric_cols}

    Sample data:
    {df.head().to_json()}

    Available tools:
    - correlation (2 numeric columns)
    - regression (2 numeric columns)
    - anomaly_detection (1 numeric column)
    - distribution (1 numeric column)
    - t_test (2 numeric columns)

    Rules:
    - Use only numeric columns
    - Avoid ID-like columns
    - Avoid duplicate analyses
    - Choose meaningful relationships

    Return STRICT JSON list:

    [
      {{
        "tool": "correlation",
        "col1": "colA",
        "col2": "colB"
      }}
    ]
    """

    # -----------------------------
    # 🛡️ SAFE PLAN GENERATION
    # -----------------------------
    try:
        decision = llm.invoke(prompt).content.strip()
        plan = json.loads(decision)

        if not isinstance(plan, list):
            raise ValueError("Invalid plan format")

    except Exception as e:
        logger.warning(f"Invalid stats plan: {e}")
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
                    results.setdefault("correlation", []).append(
                        correlation_test_tool.invoke({
                            "input_json": json.dumps({
                                "data": data_json,
                                "col1": col1,
                                "col2": col2
                            })
                        })
                    )

            # -----------------------------
            # 📈 REGRESSION
            # -----------------------------
            elif tool_name == "regression":

                col1 = safe_column(item.get("col1"), df)
                col2 = safe_column(item.get("col2"), df)

                if col1 and col2:
                    results.setdefault("regression", []).append(
                        regression_tool.invoke({
                            "input_json": json.dumps({
                                "data": data_json,
                                "feature": col1,
                                "target": col2
                            })
                        })
                    )

            # -----------------------------
            # 🚨 ANOMALY
            # -----------------------------
            elif tool_name == "anomaly_detection":

                column = safe_column(item.get("column"), df)

                if column:
                    results.setdefault("anomaly", []).append(
                        anomaly_detection_tool.invoke({
                            "input_json": json.dumps({
                                "data": data_json,
                                "column": column
                            })
                        })
                    )

            # -----------------------------
            # 📊 DISTRIBUTION
            # -----------------------------
            elif tool_name == "distribution":

                column = safe_column(item.get("column"), df)

                if column:
                    results.setdefault("distribution", []).append(
                        distribution_tool.invoke({
                            "input_json": json.dumps({
                                "data": data_json,
                                "column": column
                            })
                        })
                    )

            # -----------------------------
            # 🧪 T-TEST
            # -----------------------------
            elif tool_name == "t_test":

                col1 = safe_column(item.get("col1"), df)
                col2 = safe_column(item.get("col2"), df)

                if col1 and col2:
                    results.setdefault("t_test", []).append(
                        t_test_tool.invoke({
                            "input_json": json.dumps({
                                "data": data_json,
                                "col1": col1,
                                "col2": col2
                            })
                        })
                    )

        except Exception as e:
            logger.error(f"{tool_name} failed: {e}")

    # -----------------------------
    # ✅ SINGLE LOG (FIXED)
    # -----------------------------
    logger.info("Stats analysis completed")

    # -----------------------------
    # 🧠 SUMMARY
    # -----------------------------
    summary_prompt = f"""
    You are a business analyst.

    Based on statistical results:

    {results}

    Generate:
    - 3 key insights
    - 2 relationships
    - 1 anomaly (if any)

    Keep it simple and business-focused.
    """

    try:
        summary = llm.invoke(summary_prompt).content.strip()
    except Exception as e:
        logger.error(f"Stats summary failed: {e}")
        summary = "⚠️ Unable to generate summary"

    return {
        "plan": plan,
        "results": results,
        "summary": summary
    }