def dataframe_to_text(df):
    return df.astype(str).apply(lambda x: " | ".join(x), axis=1).tolist()