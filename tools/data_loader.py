from langchain.tools import tool
import json
import pandas as pd
import io

def load_data(file):

    # -----------------------------
    # 🔁 RESET POINTER (IMPORTANT)
    # -----------------------------
    if hasattr(file, "seek"):
        file.seek(0)

    # -----------------------------
    # 🧠 GET FILE NAME SAFELY
    # -----------------------------
    file_name = getattr(file, "name", "")

    # -----------------------------
    # 📂 HANDLE BASED ON TYPE
    # -----------------------------
    if file_name.endswith(".csv") or isinstance(file, io.StringIO):
        return pd.read_csv(file)

    elif file_name.endswith(".xlsx"):
        return pd.read_excel(file)

    # fallback: try csv
    try:
        return pd.read_csv(file)
    except Exception:
        raise ValueError("Unsupported file format")
    
@tool
def load_data_tool(file_info: str) -> str:
    """
    Load dataset from file.
    Input: file path or file-like object info (string)
    Output: dataframe in JSON format
    """

    try:
        # NOTE: Streamlit file is not directly usable inside tool
        # so we will pass file separately (explained below)

        return "Tool expects file to be preloaded in agent context"

    except Exception as e:
        return str(e)