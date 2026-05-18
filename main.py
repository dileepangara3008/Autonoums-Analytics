import os
import logging
import warnings
import io

warnings.filterwarnings("ignore")
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
logging.getLogger("transformers").setLevel(logging.ERROR)

import streamlit as st
import pandas as pd

from core.state import AgentState
from agents.ingestion_agent import ingestion_agent
from graph.builder import build_graph
from agents.chat_agent import run_chat_agent

# -----------------------------
# 🚀 INIT GRAPH
# -----------------------------
graph = build_graph()

# -----------------------------
# 🧠 SESSION STATE
# -----------------------------
if "state" not in st.session_state:
    st.session_state.state = None

# -----------------------------
# 🎯 PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Autonomous Analytics AI",
    layout="wide"
)

st.title("🚀 Autonomous Analytics Platform")

# -----------------------------
# 📂 SIDEBAR
# -----------------------------
st.sidebar.title("📂 Controls")

file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

page = st.sidebar.radio(
    "Navigate",
    ["📊 Dashboard", "💬 Chat"]
)

# -----------------------------
# ▶️ START PIPELINE
# -----------------------------
if file and st.sidebar.button("Start Pipeline"):

    state = AgentState()
    state.file = file

    # 🔥 KEEP YOUR ORIGINAL INGESTION
    state = ingestion_agent(state)

    st.session_state.state = state
    st.rerun()

# -----------------------------
# 🧠 MAIN STATE
# -----------------------------
state = st.session_state.state

if state:

    df = state.cleaned_data if state.cleaned_data is not None else state.dataset

    # ======================================================
    # 📊 DASHBOARD
    # ======================================================
    if page == "📊 Dashboard":

        st.subheader("📊 Dashboard")

        # -----------------------------
        # 🔴 HITL (UNCHANGED LOGIC)
        # -----------------------------
        if state.waiting_for_input and state.current_stage == "CLEANING":

            st.warning("⚠️ Missing values detected. Choose cleaning strategy.")

            col1, col2, col3 = st.columns(3)

            selected_option = None

            if col1.button("🗑 Drop"):
                selected_option = "drop"

            if col2.button("🧮 Fill"):
                selected_option = "fill"

            if col3.button("⏭ Skip"):
                selected_option = "skip"

            if selected_option:

                from tools.cleaning import cleaning_tool

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

        # -----------------------------
        # 📊 METRICS
        # -----------------------------
        if df is not None:

            c1, c2, c3 = st.columns(3)

            c1.metric("Rows", df.shape[0])
            c2.metric("Columns", df.shape[1])
            c3.metric("Missing", df.isnull().sum().sum())

        # -----------------------------
        # 📊 DATA PREVIEW
        # -----------------------------
        if df is not None:
            st.subheader("📂 Dataset Preview")
            st.dataframe(df.head(), use_container_width=True)

        # -----------------------------
        # 📊 EDA + STATS
        # -----------------------------
        col1, col2 = st.columns(2)

        with col1:
            if state.eda_results:
                st.subheader("📊 EDA")
                st.write(state.eda_results)

        with col2:
            if state.statistical_results:
                st.subheader("📈 Stats")
                st.write(state.statistical_results)

        # -----------------------------
        # 📊 VISUALIZATIONS
        # -----------------------------
        if state.charts:
            st.subheader("📊 Visualizations")

            cols = st.columns(2)

            for i, chart in enumerate(state.charts):
                if "figure" in chart:
                    cols[i % 2].plotly_chart(
                        chart["figure"],
                        use_container_width=True
                    )

        # -----------------------------
        # 💡 INSIGHTS
        # -----------------------------
        if state.insights:

            st.subheader("💡 Insights")

            for i in state.insights.get("key_insights", []):
                st.success(i)

            for i in state.insights.get("relationships", []):
                st.info(i)

            for i in state.insights.get("anomalies", []):
                st.warning(i)

            for i in state.insights.get("recommendations", []):
                st.write("•", i)

        # -----------------------------
        # ❌ ERRORS
        # -----------------------------
        if state.errors:
            st.error(state.errors)

    # ======================================================
    # 💬 CHAT
    # ======================================================
    elif page == "💬 Chat":

        st.subheader("💬 Chat with your Data")

        # -----------------------------
        # 🧠 HISTORY
        # -----------------------------
        if state.chat_history:

            for chat in state.chat_history[-5:]:

                with st.chat_message("user"):
                    st.write(chat["user"])

                with st.chat_message("assistant"):

                    if isinstance(chat["assistant"], dict) and chat["assistant"].get("type") == "chart":

                        st.write(chat["assistant"]["text"])

                        if chat["assistant"].get("figure"):
                            st.plotly_chart(
                                chat["assistant"]["figure"],
                                use_container_width=True
                            )

                    else:
                        st.write(chat["assistant"])

        # -----------------------------
        # 💬 INPUT
        # -----------------------------
        user_query = st.chat_input("Ask anything...")

        if user_query:

            with st.chat_message("user"):
                st.write(user_query)

            response = run_chat_agent(user_query, state)

            with st.chat_message("assistant"):

                if isinstance(response, dict) and response.get("type") == "chart":

                    st.write(response["text"])

                    if response.get("figure"):
                        st.plotly_chart(
                            response["figure"],
                            use_container_width=True
                        )

                else:
                    st.write(response)

            st.session_state.state = state
            st.rerun()