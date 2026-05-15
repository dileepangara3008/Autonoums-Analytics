def supervisor(state):

    # -----------------------------
    # 🔴 HITL PRIORITY
    # -----------------------------
    if state.waiting_for_input:
        return "HITL"

    # -----------------------------
    # 🟢 START
    # -----------------------------
    if state.current_stage == "START":
        return "INGESTION"

    # -----------------------------
    # 🧹 CLEANING
    # -----------------------------
    if state.current_stage == "CLEANING":
        return "HITL"

    # -----------------------------
    # 🔍 EDA (ONLY IF NOT DONE)
    # -----------------------------
    if state.eda_results is None:
        return "EDA"

    # -----------------------------
    # 📊 STATS
    # -----------------------------
    if state.statistical_results is None:
        return "STATS"

    # -----------------------------
    # 📈 VIZ
    # -----------------------------
    if not state.charts:
        return "VIZ"

    # -----------------------------
    # 💡 INSIGHTS
    # -----------------------------
    if state.insights is None:
        return "INSIGHTS"

    # -----------------------------
    # 🛑 DONE
    # -----------------------------
    return "__end__"