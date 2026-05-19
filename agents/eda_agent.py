from core.config import get_llm
from tools.eda_tools import (
    descriptive_statistics_tool,
    missing_values_tool,
    correlation_analysis_tool,
    categorical_summary_tool
)
import json
from langsmith import traceable

@traceable(name="EDA Agent")
def run_eda_agent(df):

    llm = get_llm()

    # -----------------------------
    # 🧠 DECIDE WHICH TOOLS
    # -----------------------------
    prompt = f"""
    You are a data analyst.

    Based on dataset, decide which tools to use.

    Available tools:
    - descriptive_statistics
    - missing_values
    - correlation
    - categorical_summary

    Rules:
    - Always include descriptive_statistics
    - Include missing_values if any nulls exist
    - Include correlation if numeric columns exist
    - Include categorical_summary if categorical columns exist

    Return JSON list like:
    ["descriptive_statistics", "correlation"]

    Dataset sample:
    {df.head().to_json()}
    """

    decision = llm.invoke(prompt).content.strip()

    try:
        tools_to_use = json.loads(decision)
    except:
        tools_to_use = ["descriptive_statistics"]

    # -----------------------------
    # 🧰 TOOL EXECUTION
    # -----------------------------
    results = {}

    data_json = df.to_json()

    for tool_name in tools_to_use:

        try:
            if tool_name == "descriptive_statistics":
                results["descriptive_statistics"] = descriptive_statistics_tool.invoke({
                    "data": data_json
                })

            elif tool_name == "missing_values":
                results["missing_values"] = missing_values_tool.invoke({
                    "data": data_json
                })

            elif tool_name == "correlation":
                results["correlation"] = correlation_analysis_tool.invoke({
                    "data": data_json
                })

            elif tool_name == "categorical_summary":

                # pick first categorical column automatically
                cat_cols = df.select_dtypes(include="object").columns

                if len(cat_cols) > 0:
                    results["categorical_summary"] = categorical_summary_tool.invoke({
                        "input_json": json.dumps({
                            "data": data_json,
                            "column": cat_cols[0]
                        })
                    })

        except Exception as e:
            results[tool_name] = f"Error: {str(e)}"

    # -----------------------------
    # 🧠 FINAL SUMMARY
    # -----------------------------
    summary_prompt = f"""
    Based on the following analysis results:

    {results}

    Generate a clean EDA summary with:
    - key observations
    - patterns
    - data quality issues
    """

    final_summary = llm.invoke(summary_prompt).content

    return {
        "tools_used": tools_to_use,
        "raw_results": results,
        "summary": final_summary
    }