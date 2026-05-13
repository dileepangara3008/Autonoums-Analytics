from tools.cleaning import clean_missing

def handle_hitl(state, user_input):
    
    if state.current_stage == "POST_INGESTION":
        strategy = user_input.get("strategy", "skip")
        
        if strategy != "skip":
            state.cleaned_data = clean_missing(state.dataset, strategy)
        else:
            state.cleaned_data = state.dataset
        
        state.waiting_for_input = False
        state.current_stage = "EDA_READY"
    
    return state