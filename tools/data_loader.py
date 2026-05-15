from langchain.tools import tool
import json
import pandas as pd

def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    elif file.name.endswith(".xlsx"):
        return pd.read_excel(file)
    else:
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