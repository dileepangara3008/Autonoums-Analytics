from tools.cleaning import cleaning_tool
import pandas as pd
import io

def test_cleaning_drop():

    df = pd.DataFrame({
        "a": [1, None]
    })

    result = cleaning_tool.invoke({
        "data": df.to_json(),
        "strategy": "drop"
    })

    cleaned = pd.read_json(io.StringIO(result))

    assert cleaned.isnull().sum().sum() == 0

def test_cleaning_fill():

    df = pd.DataFrame({"a": [1, None]})

    result = cleaning_tool.invoke({
        "data": df.to_json(),
        "strategy": "fill"
    })

    cleaned = pd.read_json(io.StringIO(result))

    # no nulls after fill
    assert cleaned.isnull().sum().sum() == 0