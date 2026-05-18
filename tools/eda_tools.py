from langchain.tools import tool
import pandas as pd
import numpy as np
import json
import io
import warnings

warnings.filterwarnings("ignore")
# -----------------------------
# 📊 DESCRIPTIVE STATISTICS
# -----------------------------
@tool
def descriptive_statistics_tool(data: str) -> str:
    """
    Use this tool to get descriptive statistics of the dataset.
    Input: JSON string of dataframe.
    """

    try:
        df = pd.read_json(io.StringIO(data))

        stats = df.describe(include='all')

        # 🔥 FIX: convert datetime safely
        stats = stats.applymap(lambda x: str(x) if isinstance(x, pd.Timestamp) else x)

        return json.dumps({
            "type": "descriptive_statistics",
            "shape": df.shape,
            "summary": stats.to_dict()
        })

    except Exception as e:
        return json.dumps({"error": str(e)})


# -----------------------------
# 🔍 MISSING VALUES
# -----------------------------
@tool
def missing_values_tool(data: str) -> str:
    """
    Use this tool to analyze missing values in dataset.
    """

    try:
        df = pd.read_json(data)

        missing = df.isnull().sum()
        missing = missing[missing > 0]

        return json.dumps({
            "type": "missing_values",
            "missing": missing.to_dict()
        })

    except Exception as e:
        return json.dumps({"error": str(e)})


# -----------------------------
# 📈 CORRELATION ANALYSIS
# -----------------------------
@tool
def correlation_analysis_tool(data: str) -> str:
    """
    Use this tool to compute correlation between numeric columns.
    """

    try:
        df = pd.read_json(data)

        numeric_df = df.select_dtypes(include=np.number)

        if numeric_df.shape[1] < 2:
            return json.dumps({
                "type": "correlation",
                "message": "Not enough numeric columns"
            })

        corr = numeric_df.corr()

        return json.dumps({
            "type": "correlation",
            "matrix": corr.to_dict()
        })

    except Exception as e:
        return json.dumps({"error": str(e)})


# -----------------------------
# 🧾 CATEGORICAL SUMMARY
# -----------------------------
@tool
def categorical_summary_tool(input_json: str) -> str:
    """
    Use this tool to get value counts of a categorical column.
    Input must contain:
    {
        "data": "<df_json>",
        "column": "<column_name>"
    }
    """

    try:
        payload = json.loads(input_json)

        df = pd.read_json(payload["data"])
        column = payload["column"]

        if column not in df.columns:
            return json.dumps({
                "type": "categorical_summary",
                "error": f"Column '{column}' not found"
            })

        counts = df[column].value_counts()

        return json.dumps({
            "type": "categorical_summary",
            "column": column,
            "counts": counts.to_dict()
        })

    except Exception as e:
        return json.dumps({"error": str(e)})