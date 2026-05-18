import os
import logging
import warnings

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
graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
# -----------------------------
# 🧠 SESSION STATE
# -----------------------------
if "state" not in st.session_state:
    st.session_state.state = None

# -----------------------------
# 🎯 UI
# -----------------------------
st.set_page_config(page_title="Autonomous Analytics AI", layout="wide")
st.title("🚀 Autonomous Analytics Platform")

file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

# -----------------------------
# ▶️ START PIPELINE
# -----------------------------
if file and st.sidebar.button("Start Pipeline"):
    state = AgentState()
    state.file = file

    # 🔥 CALL INGESTION DIRECTLY (CRITICAL FIX)
    state = ingestion_agent(state)

    print("AFTER INGESTION:", state.current_stage, state.waiting_for_input)

    st.session_state.state = state
    st.rerun()
# -----------------------------
# 🧠 MAIN STATE
# -----------------------------
state = st.session_state.state

if state:

    st.write("### 🧠 Stage:", state.current_stage)
    st.write("### ⏸ Waiting:", state.waiting_for_input)

    df = state.cleaned_data if state.cleaned_data is not None else state.dataset

    # -----------------------------
    # 🔴 HITL CHECKPOINT (CLEANING)
    # -----------------------------
    if state.waiting_for_input and state.current_stage == "CLEANING":

        st.warning("⚠️ Missing values detected. Choose cleaning strategy.")

        option = st.selectbox("Strategy", ["drop", "fill", "skip"])

        if st.button("Apply Cleaning"):

            from tools.cleaning import cleaning_tool

            if option != "skip":
                cleaned = cleaning_tool.invoke({
                    "data": state.dataset.to_json(),
                    "strategy": option
                })
                state.cleaned_data = pd.read_json(cleaned)
            else:
                state.cleaned_data = state.dataset

            # 🔥 RESUME PIPELINE
            state.waiting_for_input = False
            state.current_stage = "EDA"

            # 🔥 CONTINUE FULL PIPELINE
            result = graph.invoke(state)
            state = AgentState(**result) if isinstance(result, dict) else result

            st.session_state.state = state
            st.rerun()

    # -----------------------------
    # 📊 OUTPUT
    # -----------------------------
    st.divider()
    st.header("📊 Results")

    if df is not None:
        st.subheader("Dataset Preview")
        st.dataframe(df.head())

    if state.eda_results:
        st.subheader("📊 EDA Results")
        st.write(state.eda_results)

    if state.statistical_results:
        st.subheader("📈 Statistical Results")
        st.write(state.statistical_results)

    if state.charts:
        st.subheader("📊 Visualizations")

        cols = st.columns(2)

        for i, chart in enumerate(state.charts):

            if "figure" in chart:
                cols[i % 2].plotly_chart(
                    chart["figure"],
                    use_container_width=True
                )

    if state.insights:

        st.subheader("💡 Key Insights")
        for i in state.insights.get("key_insights", []):
            st.write("•", i)

        st.subheader("🔗 Relationships")
        for i in state.insights.get("relationships", []):
            st.write("•", i)

        st.subheader("🚨 Anomalies")
        for i in state.insights.get("anomalies", []):
            st.write("•", i)

        st.subheader("📌 Recommendations")
        for i in state.insights.get("recommendations", []):
            st.write("•", i)

    if state.errors:
        st.subheader("❌ Errors")
        st.error(state.errors)
    
    # -----------------------------
    # 💬 CHAT WITH DATA
    # -----------------------------
    st.divider()
    st.header("💬 Chat with your Data")

    with st.form("chat_form", clear_on_submit=True):

        user_query = st.text_input("Ask anything about your dataset")

        submitted = st.form_submit_button("Ask")

        if submitted and user_query:

            from agents.chat_agent import run_chat_agent

            response = run_chat_agent(user_query, state)

            st.write("### 🤖 Answer")
            # -----------------------------
            # 📊 HANDLE CHART RESPONSE
            # -----------------------------
            if isinstance(response, dict) and response.get("type") == "chart":

                # show explanation
                st.write(response.get("text", ""))

                # show chart
                if response.get("figure"):
                    st.plotly_chart(response["figure"], use_container_width=True)

            # -----------------------------
            # 🧠 HANDLE TEXT RESPONSE
            # -----------------------------
            else:
                st.write(response)

            # save updated state
            st.session_state.state = state

    # -----------------------------
    # 🧠 CHAT HISTORY
    # -----------------------------
    if state.chat_history:

        st.subheader("🧠 Conversation")

        for chat in reversed(state.chat_history[-5:]):
            st.markdown(f"**🧑 You:** {chat['user']}")
            st.markdown(f"**🤖 AI:** {chat['assistant']}")
            st.markdown("---")