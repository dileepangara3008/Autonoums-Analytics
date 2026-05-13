def checkpoint_post_ingestion(state):
    return {
        "message": "Dataset loaded. Clean missing values?",
        "options": ["drop", "fill", "skip"]
    }