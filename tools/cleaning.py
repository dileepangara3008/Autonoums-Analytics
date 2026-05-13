def clean_missing(df, strategy="drop"):
    if strategy == "drop":
        return df.dropna()
    elif strategy == "fill":
        return df.fillna(df.mean(numeric_only=True))
    return df