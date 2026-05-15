def router_agent(state):
    query = state.query.lower()

    try:
        if any(word in query for word in ["average", "trend", "correlation", "regression"]):
            state.query_type = "analytics"
        elif any(word in query for word in ["what", "who", "when", "explain"]):
            state.query_type = "rag"
        else:
            state.query_type = "hybrid"

        # 🔴 CHECKPOINT 3
        state.current_stage = "POST_ROUTING"
        state.waiting_for_input = True

    except Exception as e:
        state.errors.append(str(e))

    return state