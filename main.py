# app/main.py

import streamlit as st
from core.state import AgentState
from graph.builder import build_graph

from app.components.sidebar import render_sidebar
from app.pages.dashboard import render_dashboard
from app.pages.chat import render_chat

import logging
import warnings
import os

warnings.filterwarnings("ignore")
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
logging.getLogger("transformers").setLevel(logging.ERROR)

st.set_page_config(page_title="Autonomous Analytics AI", layout="wide")
st.title("🚀 Autonomous Analytics Platform")

graph = build_graph()

state, page = render_sidebar()

if state:
    if page == "📊 Dashboard":
        render_dashboard(state, graph)

    elif page == "💬 Chat":
        render_chat(state)