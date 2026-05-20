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
    You are an expert data analyst.

    Your task is to decide which analysis tools to run on a dataset.

    AVAILABLE TOOLS:
    - descriptive_statistics
    - missing_values
    - correlation
    - categorical_summary

    DATASET INFORMATION:

    Columns:
    {df.columns.tolist()}

    Numeric Columns:
    {df.select_dtypes(include="number").columns.tolist()}

    Categorical Columns:
    {df.select_dtypes(include="object").columns.tolist()}

    Missing Values Count (per column):
    {df.isnull().sum().to_dict()}

    RULES:
    - ALWAYS include "descriptive_statistics"
    - Include "missing_values" ONLY if any column has missing values (> 0)
    - Include "correlation" ONLY if there are 2 or more numeric columns
    - Include "categorical_summary" ONLY if categorical columns exist
    - DO NOT include unnecessary tools
    - DO NOT invent tools

    OUTPUT FORMAT (STRICT):
    Return ONLY a JSON list.
    Example:
    ["descriptive_statistics", "correlation"]

    DO NOT include explanations or extra text.
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