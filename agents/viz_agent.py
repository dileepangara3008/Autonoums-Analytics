from core.config import get_llm
from tools.viz_tools import (
    histogram_tool,
    scatter_tool,
    line_chart_tool,
    bar_chart_tool,
    pie_chart_tool,
    box_plot_tool,
    heatmap_tool
)
import json


# -----------------------------
# 🔐 SAFE COLUMN VALIDATION
# -----------------------------
def safe_column(col, df):
    return col if col in df.columns else None


def is_useful_column(col):
    bad_keywords = ["id", "index"]
    return not any(k in col.lower() for k in bad_keywords)


def run_viz_agent(df, eda_results=None, stats_results=None):

    llm = get_llm()
    data_json = df.to_json()

    numeric_cols = [
        col for col in df.select_dtypes(include="number").columns
        if is_useful_column(col)
    ]

    categorical_cols = [
        col for col in df.select_dtypes(include="object").columns
        if is_useful_column(col)
    ]

    # -----------------------------
    # 🧠 CONTEXT FOR LLM
    # -----------------------------
    eda_summary = json.dumps(eda_results) if eda_results else "None"
    stats_summary = json.dumps(stats_results) if stats_results else "None"

    # -----------------------------
    # 🧠 SMART PROMPT
    # -----------------------------
    prompt = f"""
    You are a data visualization expert.

    You are given:
    - dataset schema
    - EDA results
    - statistical analysis results

    Dataset columns:
    {df.columns.tolist()}

    Numeric columns:
    {numeric_cols}

    Categorical columns:
    {categorical_cols}

    EDA Results:
    {eda_summary}

    Statistical Results:
    {stats_summary}

    Your task:
    Generate a COMPLETE and MEANINGFUL visualization plan.

    Think step-by-step:

    1. Distribution → show how data is spread
    2. Relationships → show correlations or trends
    3. Comparisons → show categorical differences
    4. Insights from stats → highlight important findings

    Rules:
    - If correlation exists → include scatter plot
    - If regression exists → include line plot
    - If anomalies exist → include box plot
    - If multiple numeric columns → include heatmap
    - Always include at least 3 different types of charts
    - Avoid id/index columns

    Return STRICT JSON list:

    [
      {{"type": "histogram", "column": "col1"}},
      {{"type": "scatter", "x": "col1", "y": "col2"}},
      {{"type": "bar", "x": "category", "y": "col1"}},
      {{"type": "heatmap"}}
    ]

    Return ONLY valid JSON.
    """

    decision = llm.invoke(prompt).content.strip()

    try:
        chart_plan = json.loads(decision)
    except:
        chart_plan = []

    # -----------------------------
    # 🔁 FALLBACK
    # -----------------------------
    if not chart_plan:

        chart_plan = []

        if numeric_cols:
            chart_plan.append({
                "type": "histogram",
                "column": numeric_cols[0]
            })

        if len(numeric_cols) >= 2:
            chart_plan.append({
                "type": "scatter",
                "x": numeric_cols[0],
                "y": numeric_cols[1]
            })

        if len(numeric_cols) >= 2:
            chart_plan.append({"type": "heatmap"})

    charts = []

    # -----------------------------
    # ⚙️ EXECUTION
    # -----------------------------
    for item in chart_plan:

        try:
            chart_type = item.get("type")
            res = None

            if chart_type == "histogram":
                col = safe_column(item.get("column"), df)
                if col and is_useful_column(col):
                    res = histogram_tool.invoke({
                        "input_json": json.dumps({"data": data_json, "column": col})
                    })

            elif chart_type == "scatter":
                x = safe_column(item.get("x"), df)
                y = safe_column(item.get("y"), df)
                if x and y:
                    res = scatter_tool.invoke({
                        "input_json": json.dumps({"data": data_json, "x": x, "y": y})
                    })

            elif chart_type == "line":
                x = safe_column(item.get("x"), df)
                y = safe_column(item.get("y"), df)
                if x and y:
                    res = line_chart_tool.invoke({
                        "input_json": json.dumps({"data": data_json, "x": x, "y": y})
                    })

            elif chart_type == "bar":
                x = safe_column(item.get("x"), df)
                y = safe_column(item.get("y"), df)
                if x and y:
                    res = bar_chart_tool.invoke({
                        "input_json": json.dumps({"data": data_json, "x": x, "y": y})
                    })

            elif chart_type == "pie":
                names = safe_column(item.get("names"), df)
                values = safe_column(item.get("values"), df)
                if names and values:
                    res = pie_chart_tool.invoke({
                        "input_json": json.dumps({"data": data_json, "names": names, "values": values})
                    })

            elif chart_type == "box":
                col = safe_column(item.get("column"), df)
                if col:
                    res = box_plot_tool.invoke({
                        "input_json": json.dumps({"data": data_json, "column": col})
                    })

            elif chart_type == "heatmap" and len(numeric_cols) >= 2:
                res = heatmap_tool.invoke({
                    "input_json": json.dumps({"data": data_json})
                })

            if isinstance(res, dict) and "figure" in res:
                charts.append(res)

        except Exception as e:
            charts.append({"error": str(e)})

    return charts