from langchain.tools import tool
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np
import json
import io

# -----------------------------
# 📊 HISTOGRAM
# -----------------------------
@tool
def histogram_tool(input_json: str):
    """
    histogram viz tool
    """

    payload = json.loads(input_json)
    df = pd.read_json(io.StringIO(payload["data"]))
    column = payload["column"]

    df[column] = pd.to_numeric(df[column], errors="coerce")

    fig = px.histogram(
        df,
        x=column,
        nbins=20,
        title=f"Distribution of {column}"
    )

    return {
        "type": "histogram",
        "figure": fig
    }


# -----------------------------
# 📈 SCATTER
# -----------------------------
@tool
def scatter_tool(input_json: str):
    """
    scatter
    """
    try:
        payload = json.loads(input_json)
        df = pd.read_json(io.StringIO(payload["data"]))
        x, y = payload["x"], payload["y"]

        fig = px.scatter(df, x=x, y=y, title=f"{x} vs {y}")

        return {"type": "scatter", "x": x, "y": y, "figure": fig}

    except Exception as e:
        return {"error": str(e)}


# -----------------------------
# 📉 LINE
# -----------------------------
@tool
def line_chart_tool(input_json: str):
    """
    line chart
    """
    try:
        payload = json.loads(input_json)
        df = pd.read_json(io.StringIO(payload["data"]))
        x, y = payload["x"], payload["y"]

        fig = px.line(df, x=x, y=y, title=f"{y} over {x}")

        return {"type": "line", "x": x, "y": y, "figure": fig}

    except Exception as e:
        return {"error": str(e)}


# -----------------------------
# 📊 BAR
# -----------------------------
@tool
def bar_chart_tool(input_json: str):
    """
    bar chart
    """
    try:
        payload = json.loads(input_json)
        df = pd.read_json(io.StringIO(payload["data"]))
        x, y = payload["x"], payload["y"]

        fig = px.bar(df, x=x, y=y, title=f"{y} by {x}")

        return {"type": "bar", "x": x, "y": y, "figure": fig}

    except Exception as e:
        return {"error": str(e)}


# -----------------------------
# 🥧 PIE
# -----------------------------
@tool
def pie_chart_tool(input_json: str):
    """
    pie chart
    """
    try:
        payload = json.loads(input_json)
        df = pd.read_json(io.StringIO(payload["data"]))
        names, values = payload["names"], payload["values"]

        fig = px.pie(df, names=names, values=values)

        return {"type": "pie", "names": names, "values": values, "figure": fig}

    except Exception as e:
        return {"error": str(e)}


# -----------------------------
# 📦 BOX
# -----------------------------
@tool
def box_plot_tool(input_json: str):
    """
    box plot 
    """
    try:
        payload = json.loads(input_json)
        df = pd.read_json(io.StringIO(payload["data"]))
        column = payload["column"]

        fig = px.box(df, y=column)

        return {"type": "box", "column": column, "figure": fig}

    except Exception as e:
        return {"error": str(e)}


# -----------------------------
# 🔥 HEATMAP
# -----------------------------
@tool
def heatmap_tool(input_json: str):
    """
    heatmap
    """
    try:
        payload = json.loads(input_json)
        df = pd.read_json(io.StringIO(payload["data"]))

        numeric_df = df.select_dtypes(include=np.number)
        corr = numeric_df.corr()

        fig = ff.create_annotated_heatmap(
            z=corr.values,
            x=list(corr.columns),
            y=list(corr.index),
            annotation_text=corr.round(2).values
        )

        return {"type": "heatmap", "figure": fig}

    except Exception as e:
        return {"error": str(e)}