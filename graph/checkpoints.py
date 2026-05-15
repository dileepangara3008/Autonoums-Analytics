def checkpoint_post_ingestion(state):
    return {
        "message": "Dataset loaded. Clean missing values?",
        "options": ["drop", "fill", "skip"]
    }

def checkpoint_post_eda(state):
    return {
        "message": "EDA complete. Strong correlations found. Proceed to statistical analysis?",
        "options": ["yes", "focus_columns", "skip"]
    }

def checkpoint_post_routing(state):
    return {
        "message": f"Detected query type: {state.query_type}. Proceed?",
        "options": ["yes", "change"]
    }