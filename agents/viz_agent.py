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
import re


# -----------------------------
# 🔐 SAFE COLUMN VALIDATION
# -----------------------------
def safe_column(col, df):
    return col if col in df.columns else None


def is_valid_column(col, df):

    if col not in df.columns:
        return False

    # ❌ remove id/index
    if any(k in col.lower() for k in ["id", "index"]):
        return False

    # ❌ constant column
    if df[col].nunique() <= 1:
        return False

    # ❌ too many nulls
    if df[col].isnull().mean() > 0.5:
        return False

    return True


# -----------------------------
# 🔍 VALIDATE LLM OUTPUT
# -----------------------------
def validate_chart(item, df):

    chart_type = item.get("type")

    if chart_type == "histogram":
        return is_valid_column(item.get("column"), df)

    if chart_type in ["scatter", "line"]:
        return (
            is_valid_column(item.get("x"), df) and
            is_valid_column(item.get("y"), df)
        )

    if chart_type == "bar":
        return (
            is_valid_column(item.get("x"), df) and
            is_valid_column(item.get("y"), df)
        )

    if chart_type == "box":
        return is_valid_column(item.get("column"), df)

    if chart_type == "pie":
        return (
            is_valid_column(item.get("names"), df) and
            is_valid_column(item.get("values"), df)
        )

    if chart_type == "heatmap":
        return True

    return False


# -----------------------------
# 🔥 FIX: EXTRACT JSON FROM LLM
# -----------------------------
def extract_json(text):
    try:
        # extract JSON inside ```json ... ```
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))

        # fallback direct parse
        return json.loads(text)

    except Exception as e:
        print("JSON extraction failed:", e)
        return []


# -----------------------------
# 🚀 MAIN AGENT
# -----------------------------
def run_viz_agent(df, eda_results=None, stats_results=None):

    llm = get_llm()
    data_json = df.to_json()

    # -----------------------------
    # 📊 FILTER VALID COLUMNS
    # -----------------------------
    numeric_cols = [
        col for col in df.select_dtypes(include="number").columns
        if is_valid_column(col, df)
    ]

    categorical_cols = [
        col for col in df.select_dtypes(include="object").columns
        if is_valid_column(col, df)
    ]

    # -----------------------------
    # 🧠 CONTEXT
    # -----------------------------
    eda_summary = json.dumps(eda_results) if eda_results else "None"
    stats_summary = json.dumps(stats_results) if stats_results else "None"

    # -----------------------------
    # 🧠 PROMPT
    # -----------------------------
    prompt = f"""
    You are a data visualization expert.

    You are given:
    - dataset schema
    - EDA results
    - statistical analysis results

    Dataset columns:
    {df.columns.tolist()}

    Valid Numeric columns:
    {numeric_cols}

    Valid Categorical columns:
    {categorical_cols}

    EDA Results:
    {eda_summary}

    Statistical Results:
    {stats_summary}

    Your task:
    Create a DASHBOARD (not random charts).

    Requirements:
    - Generate 4–6 charts
    - Each chart must show DIFFERENT insight

    Guidelines:
    - Use EDA → distributions
    - Use Stats → relationships
    - Prefer strongest relationships from stats

    Charts:
    - histogram → distribution
    - scatter → relationships
    - bar → comparison
    - box → outliers
    - heatmap → correlations

    STRICT RULES:
    - ONLY use provided columns
    - DO NOT use id/index columns
    - DO NOT invent columns
    - RETURN ONLY JSON (NO TEXT)

    Example:
    [
      {{"type": "histogram", "column": "sales"}},
      {{"type": "scatter", "x": "price", "y": "sales"}}
    ]
    """

    decision = llm.invoke(prompt).content.strip()

    print("LLM RAW OUTPUT:", decision)

    # -----------------------------
    # 🔥 FIXED PARSING
    # -----------------------------
    chart_plan = extract_json(decision)

    print("PARSED CHART PLAN:", chart_plan)

    # -----------------------------
    # 🔁 FALLBACK (ONLY IF EMPTY)
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

    # -----------------------------
    # LIMIT DASHBOARD SIZE
    # -----------------------------
    chart_plan = chart_plan[:6]

    charts = []

    # -----------------------------
    # ⚙️ EXECUTION
    # -----------------------------
    for item in chart_plan:

        if not validate_chart(item, df):
            continue

        try:
            chart_type = item.get("type")
            res = None

            if chart_type == "histogram":
                col = safe_column(item.get("column"), df)
                if col:
                    res = histogram_tool.invoke({
                        "input_json": json.dumps({
                            "data": data_json,
                            "column": col
                        })
                    })

            elif chart_type == "scatter":
                x = safe_column(item.get("x"), df)
                y = safe_column(item.get("y"), df)
                if x and y:
                    res = scatter_tool.invoke({
                        "input_json": json.dumps({
                            "data": data_json,
                            "x": x,
                            "y": y
                        })
                    })

            elif chart_type == "line":
                x = safe_column(item.get("x"), df)
                y = safe_column(item.get("y"), df)
                if x and y:
                    res = line_chart_tool.invoke({
                        "input_json": json.dumps({
                            "data": data_json,
                            "x": x,
                            "y": y
                        })
                    })

            elif chart_type == "bar":
                x = safe_column(item.get("x"), df)
                y = safe_column(item.get("y"), df)
                if x and y:
                    res = bar_chart_tool.invoke({
                        "input_json": json.dumps({
                            "data": data_json,
                            "x": x,
                            "y": y
                        })
                    })

            elif chart_type == "pie":
                names = safe_column(item.get("names"), df)
                values = safe_column(item.get("values"), df)
                if names and values:
                    res = pie_chart_tool.invoke({
                        "input_json": json.dumps({
                            "data": data_json,
                            "names": names,
                            "values": values
                        })
                    })

            elif chart_type == "box":
                col = safe_column(item.get("column"), df)
                if col:
                    res = box_plot_tool.invoke({
                        "input_json": json.dumps({
                            "data": data_json,
                            "column": col
                        })
                    })

            elif chart_type == "heatmap" and len(numeric_cols) >= 2:

                filtered_numeric = [
                    col for col in numeric_cols
                    if is_valid_column(col, df)
                ]

                res = heatmap_tool.invoke({
                    "input_json": json.dumps({
                        "data": df[filtered_numeric].to_json()
                    })
                })

            if isinstance(res, dict) and "figure" in res:
                charts.append(res)

        except Exception as e:
            charts.append({"error": str(e)})

    return charts