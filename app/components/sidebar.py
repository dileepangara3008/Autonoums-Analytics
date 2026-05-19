import streamlit as st
from core.state import AgentState
from agents.ingestion_agent import ingestion_agent

def render_sidebar():

    st.sidebar.title("📂 Controls")

    file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

    page = st.sidebar.radio("Navigate", ["📊 Dashboard", "💬 Chat"])

    if "state" not in st.session_state:
        st.session_state.state = None

    if file and st.sidebar.button("Start Pipeline"):

        state = AgentState()
        state.file = file

        state = ingestion_agent(state)

        st.session_state.state = state
        st.rerun()

    return st.session_state.state, page