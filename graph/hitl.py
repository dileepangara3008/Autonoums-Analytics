import pandas as pd
from tools.cleaning import cleaning_tool

def handle_hitl(state, user_input):

    if state.hitl_responses is None:
        state.hitl_responses = {}

    # -----------------------------
    # 🧹 CLEANING STEP (ONLY HITL YOU NEED NOW)
    # -----------------------------
    if state.current_stage == "CLEANING":

        strategy = user_input.get("strategy", "skip")
        df = state.dataset

        if strategy != "skip":
            try:

                cleaned_json = cleaning_tool.invoke({
                    "data": df.to_json(),
                    "strategy": strategy
                })

                df = pd.read_json(cleaned_json)

            except Exception as e:
                state.errors.append(f"Cleaning failed: {str(e)}")

        state.cleaned_data = df

        # ✅ RESUME PIPELINE
        state.waiting_for_input = False
        state.current_stage = "EDA_READY"

    return state