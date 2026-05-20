from langchain.tools import tool
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np
import json
import io


# ======================================================
# 🧠 COMMON PREPROCESSING (VERY IMPORTANT)
# ======================================================
def preprocess_for_chart(df, x=None, y=None, agg="sum"):

    def is_categorical(col):
        return df[col].dtype == "object"

    def is_numeric(col):
        return df[col].dtype != "object"

    try:
        # -----------------------------
        # categorical + numeric → aggregate
        # -----------------------------
        if x and y and is_categorical(x) and is_numeric(y):
            return df.groupby(x)[y].agg(agg).reset_index()

        # -----------------------------
        # categorical only → count
        # -----------------------------
        if x and not y and is_categorical(x):
            temp = df[x].value_counts().reset_index()
            temp.columns = [x, "count"]
            return temp

    except Exception as e:
        print("Preprocess error:", e)

    return df


# ======================================================
# 📊 HISTOGRAM
# ======================================================
@tool
def histogram_tool(input_json: str):
    """
    Generate a histogram for a numeric column.

    Input (JSON string):
    {
    "data": "<dataframe in JSON format>",
    "column": "<numeric column name>"
    }

    Behavior:
    - Converts column to numeric (handles invalid values)
    - Displays distribution of the column

    Output:
    {
    "type": "histogram",
    "figure": <plotly figure>
    }
    """
    try:
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

        return {"type": "histogram", "figure": fig}

    except Exception as e:
        return {"error": str(e)}


# ======================================================
# 📈 SCATTER
# ======================================================
@tool
def scatter_tool(input_json: str):
    """
    Generate a scatter plot between two numeric columns.

    Input (JSON string):
    {
    "data": "<dataframe in JSON format>",
    "x": "<column name>",
    "y": "<column name>"
    }

    Behavior:
    - Converts both columns to numeric
    - Drops rows with missing values
    - Shows relationship between variables

    Output:
    {
    "type": "scatter",
    "figure": <plotly figure>
    }
    """
    try:
        payload = json.loads(input_json)
        df = pd.read_json(io.StringIO(payload["data"]))

        x, y = payload["x"], payload["y"]

        df[x] = pd.to_numeric(df[x], errors="coerce")
        df[y] = pd.to_numeric(df[y], errors="coerce")

        df = df.dropna(subset=[x, y])

        fig = px.scatter(df, x=x, y=y, title=f"{y} vs {x}")

        return {"type": "scatter", "figure": fig}

    except Exception as e:
        return {"error": str(e)}


# ======================================================
# 📉 LINE
# ======================================================
@tool
def line_chart_tool(input_json: str):
    """
    Generate a line chart (trend analysis).

    Input (JSON string):
    {
    "data": "<dataframe in JSON format>",
    "x": "<column name>",
    "y": "<column name>"
    }

    Behavior:
    - If x is categorical → aggregates y using mean
    - Shows trend or progression of y over x

    Output:
    {
    "type": "line",
    "figure": <plotly figure>
    }
    """
    try:
        payload = json.loads(input_json)
        df = pd.read_json(io.StringIO(payload["data"]))

        x, y = payload["x"], payload["y"]

        df = preprocess_for_chart(df, x, y, agg="mean")

        fig = px.line(df, x=x, y=y, title=f"{y} over {x}")

        return {"type": "line", "figure": fig}

    except Exception as e:
        return {"error": str(e)}


# ======================================================
# 📊 BAR
# ======================================================
@tool
def bar_chart_tool(input_json: str):
    """
    Generate a bar chart for comparison.

    Input (JSON string):
    {
    "data": "<dataframe in JSON format>",
    "x": "<categorical column>",
    "y": "<numeric column>" (optional)
    }

    Behavior:
    - If x is categorical and y is numeric → aggregates using sum
    - If only x is provided → counts occurrences
    - Avoids duplicate category plotting

    Output:
    {
    "type": "bar",
    "figure": <plotly figure>
    }
    """
    try:
        payload = json.loads(input_json)
        df = pd.read_json(io.StringIO(payload["data"]))

        x = payload.get("x")
        y = payload.get("y")

        df = preprocess_for_chart(df, x, y, agg="sum")

        fig = px.bar(
            df,
            x=x,
            y=y if y else "count",
            title=f"{y or 'count'} by {x}"
        )

        return {"type": "bar", "figure": fig}

    except Exception as e:
        return {"error": str(e)}


# ======================================================
# 🥧 PIE
# ======================================================
@tool
def pie_chart_tool(input_json: str):
    """
    Generate a pie chart for proportional distribution.

    Input (JSON string):
    {
    "data": "<dataframe in JSON format>",
    "names": "<categorical column>",
    "values": "<numeric column>" (optional)
    }

    Behavior:
    - Aggregates values if needed
    - If values not provided → uses count
    - Shows proportion of categories

    Output:
    {
    "type": "pie",
    "figure": <plotly figure>
    }
    """
    try:
        payload = json.loads(input_json)
        df = pd.read_json(io.StringIO(payload["data"]))

        names = payload["names"]
        values = payload.get("values")

        df = preprocess_for_chart(df, names, values, agg="sum")

        fig = px.pie(
            df,
            names=names,
            values=values or "count"
        )

        return {"type": "pie", "figure": fig}

    except Exception as e:
        return {"error": str(e)}


# ======================================================
# 📦 BOX
# ======================================================
@tool
def box_plot_tool(input_json: str):
    """
    Generate a box plot to visualize distribution and outliers.

    Input (JSON string):
    {
    "data": "<dataframe in JSON format>",
    "column": "<numeric column>"
    }

    Behavior:
    - Converts column to numeric
    - Shows spread, quartiles, and outliers

    Output:
    {
    "type": "box",
    "figure": <plotly figure>
    }
    """
    try:
        payload = json.loads(input_json)
        df = pd.read_json(io.StringIO(payload["data"]))

        column = payload["column"]

        df[column] = pd.to_numeric(df[column], errors="coerce")

        fig = px.box(df, y=column, title=f"Distribution of {column}")

        return {"type": "box", "figure": fig}

    except Exception as e:
        return {"error": str(e)}


# ======================================================
# 🔥 HEATMAP
# ======================================================
@tool
def heatmap_tool(input_json: str):
    """
    Generate a correlation heatmap for numeric features.

    Input (JSON string):
    {
    "data": "<dataframe in JSON format>"
    }

    Behavior:
    - Selects numeric columns only
    - Computes correlation matrix
    - Displays annotated heatmap

    Output:
    {
    "type": "heatmap",
    "figure": <plotly figure>
    }
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