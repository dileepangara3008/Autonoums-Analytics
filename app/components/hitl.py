import streamlit as st
import pandas as pd
import io
from tools.cleaning import cleaning_tool
from core.state import AgentState


def handle_hitl(state, graph):

    # -----------------------------
    # 🔍 CHECK IF HITL IS NEEDED
    # -----------------------------
    if state.waiting_for_input and state.current_stage == "CLEANING":

        df = state.dataset

        if df is None:
            return state

        missing_count = df.isnull().sum().sum()

        # ======================================================
        # ⚠️ ONLY SHOW IF MISSING VALUES EXIST
        # ======================================================
        if missing_count > 0:

            st.warning(f"⚠️ Missing values detected ({missing_count} values). Choose cleaning strategy.")

            col1, col2, col3 = st.columns(3)

            selected_option = None

            if col1.button("🗑 Drop"):
                selected_option = "drop"

            if col2.button("🧮 Fill"):
                selected_option = "fill"

            if col3.button("⏭ Skip"):
                selected_option = "skip"

            if selected_option:

                if selected_option != "skip":
                    cleaned = cleaning_tool.invoke({
                        "data": state.dataset.to_json(),
                        "strategy": selected_option
                    })
                    state.cleaned_data = pd.read_json(io.StringIO(cleaned))
                else:
                    state.cleaned_data = state.dataset

                state.waiting_for_input = False
                state.current_stage = "EDA"

                result = graph.invoke(state)
                state = AgentState(**result) if isinstance(result, dict) else result

                st.session_state.state = state
                st.rerun()

        # ======================================================
        # ✅ NO MISSING VALUES → AUTO CONTINUE
        # ======================================================
        else:

            state.cleaned_data = state.dataset
            state.waiting_for_input = False
            state.current_stage = "EDA"

            result = graph.invoke(state)
            state = AgentState(**result) if isinstance(result, dict) else result

            st.session_state.state = state
            st.rerun()

    return state