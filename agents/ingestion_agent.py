from tools.data_loader import load_data
from langsmith import traceable


def ingestion_agent(state):

    try:
        df = load_data(state.file)

        state.dataset = df

        # 🔥 CHECKPOINT AFTER INGESTION
        state.current_stage = "CLEANING"
        state.waiting_for_input = True

        return state

    except Exception as e:
        state.errors.append(str(e))
        return state