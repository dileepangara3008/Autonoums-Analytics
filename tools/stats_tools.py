from langchain.tools import tool
from scipy.stats import ttest_ind, pearsonr, zscore, shapiro
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np
import json


# -----------------------------
# 📊 CORRELATION
# -----------------------------
@tool
def correlation_test_tool(input_json: str) -> str:
    """
    correlation test tool
    """
    try:
        payload = json.loads(input_json)
        df = pd.read_json(payload["data"])
        col1, col2 = payload["col1"], payload["col2"]

        temp = df[[col1, col2]].dropna()
        corr, p = pearsonr(temp[col1], temp[col2])

        return json.dumps({
            "type": "correlation",
            "col1": col1,
            "col2": col2,
            "correlation": float(corr),
            "p_value": float(p)
        })

    except Exception as e:
        return json.dumps({"error": str(e)})


# -----------------------------
# 🧪 T-TEST
# -----------------------------
@tool
def t_test_tool(input_json: str) -> str:
    """
    t test tool
    """
    try:
        payload = json.loads(input_json)
        df = pd.read_json(payload["data"])
        col1, col2 = payload["col1"], payload["col2"]

        data1 = df[col1].dropna()
        data2 = df[col2].dropna()

        stat, p = ttest_ind(data1, data2)

        return json.dumps({
            "type": "t_test",
            "col1": col1,
            "col2": col2,
            "t_stat": float(stat),
            "p_value": float(p),
            "significant": p < 0.05
        })

    except Exception as e:
        return json.dumps({"error": str(e)})


# -----------------------------
# 📈 REGRESSION
# -----------------------------
@tool
def regression_tool(input_json: str) -> str:
    """
    regression tool
    """
    try:
        payload = json.loads(input_json)
        df = pd.read_json(payload["data"])
        x = payload["feature"]
        y = payload["target"]

        temp = df[[x, y]].dropna()

        model = LinearRegression()
        model.fit(temp[[x]], temp[y])

        return json.dumps({
            "type": "regression",
            "feature": x,
            "target": y,
            "coef": float(model.coef_[0]),
            "intercept": float(model.intercept_),
            "r2": float(model.score(temp[[x]], temp[y]))
        })

    except Exception as e:
        return json.dumps({"error": str(e)})


# -----------------------------
# 🚨 ANOMALY DETECTION
# -----------------------------
@tool
def anomaly_detection_tool(input_json: str) -> str:
    """
    anomaly detection tool
    """
    try:
        payload = json.loads(input_json)
        df = pd.read_json(payload["data"])
        column = payload["column"]

        series = df[column].dropna()
        scores = np.abs(zscore(series))

        anomalies = series[scores > 3]

        return json.dumps({
            "type": "anomaly",
            "column": column,
            "count": int(len(anomalies))
        })

    except Exception as e:
        return json.dumps({"error": str(e)})


# -----------------------------
# 📊 DISTRIBUTION
# -----------------------------
@tool
def distribution_tool(input_json: str) -> str:
    """
    distribution tool
    """
    try:
        payload = json.loads(input_json)
        df = pd.read_json(payload["data"])
        column = payload["column"]

        series = df[column].dropna()

        return json.dumps({
            "type": "distribution",
            "column": column,
            "mean": float(series.mean()),
            "std": float(series.std()),
            "skew": float(series.skew())
        })

    except Exception as e:
        return json.dumps({"error": str(e)})