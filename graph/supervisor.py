def supervisor(state):
    
    if state.waiting_for_input:
        return "HITL"
    
    if state.current_stage == "POST_INGESTION":
        return "HITL"
    
    if state.current_stage == "EDA_READY":
        return "EDA_AGENT"
    
    return "END"