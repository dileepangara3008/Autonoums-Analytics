from langchain.tools import tool
import pandas as pd

@tool
def cleaning_tool(data: str, strategy: str) -> str:
    """
    Clean missing values in dataset.
    
    Args:
        data: JSON string of dataframe
        strategy: 'drop' or 'fill'
    
    Returns:
        Cleaned dataframe as JSON string
    """
    df = pd.read_json(data)

    if strategy == "drop":
        df = df.dropna()
    elif strategy == "fill":
        df = df.fillna(df.mean(numeric_only=True))

    return df.to_json()