from tools.data_loader import load_data

def ingestion_agent(state, file):
    try:
        df = load_data(file)
        
        state.dataset = df
        state.current_stage = "POST_INGESTION"
        state.waiting_for_input = True   # 🔴 CHECKPOINT
        
        return state
    
    except Exception as e:
        state.errors.append(str(e))
        return state