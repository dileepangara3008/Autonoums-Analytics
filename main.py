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

# -----------------------------
# ⚙️ Config
# -----------------------------
warnings.filterwarnings("ignore")
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
logging.getLogger("transformers").setLevel(logging.ERROR)

st.set_page_config(
    page_title="Autonomous Analytics AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# 🎨 Custom CSS
# -----------------------------
st.markdown("""
<style>

/* Main background */
.main {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}

/* Title */
h1 {
    text-align: center;
    font-size: 2.8rem !important;
    font-weight: 700;
    margin-bottom: 10px;
}

/* Glass card */
.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    box-shadow: 0px 4px 20px rgba(0,0,0,0.2);
    transition: 0.3s;
    margin-top: 25px;
}
.card:hover {
    transform: scale(1.02);
}

/* Buttons */
.stButton>button {
    border-radius: 10px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white;
    font-weight: 600;
}

/* Sidebar background */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #020617);
    padding-top: 20px;
}

/* Sidebar text */
section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Sidebar headings */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}

/* Divider */
hr {
    border: 1px solid rgba(255,255,255,0.1);
}
/* ============================= */
/* 🔥 FORCE DARK FILE UPLOADER */
/* ============================= */

/* Entire uploader block */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px dashed rgba(255,255,255,0.2);
    border-radius: 12px;
    padding: 15px;
}

/* Dropzone */
[data-testid="stFileUploaderDropzone"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 10px;
}

/* ============================= */
/* 🚨 CRITICAL FIX (Nested div override) */
/* ============================= */

/* Target ALL nested divs inside uploaded file row */
[data-testid="stFileUploaderFile"],
[data-testid="stFileUploaderFile"] > div,
[data-testid="stFileUploaderFile"] div div {
    background-color: #0f172a !important;   /* FORCE DARK */
    color: white !important;
    border-radius: 10px !important;
}

/* File name text */
[data-testid="stFileUploaderFile"] span {
    color: white !important;
    font-weight: 500;
}

/* File size text */
[data-testid="stFileUploaderFile"] small {
    color: rgba(255,255,255,0.6) !important;
}

/* Remove button (X) */
[data-testid="stFileUploaderFile"] button {
    color: white !important;
    background: transparent !important;
    border: none !important;
}

/* Icon background fix */
[data-testid="stFileUploaderFile"] svg {
    fill: white !important;
}

/* Kill any light backgrounds inside */
[data-testid="stFileUploaderFile"] * {
    background-color: transparent !important;
}

/* Re-apply dark background after reset */
[data-testid="stFileUploaderFile"] {
    background-color: #0f172a !important;
}

/* Upload button */
[data-testid="stFileUploader"] button {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white !important;
    border-radius: 8px;
    border: none;
}
            /* 🔥 Target the grey file box EXACTLY */
[data-testid="stFileUploaderFile"] > div {
    background-color: #0f172a !important;
    border-radius: 10px !important;
}

/* Force ALL inner layers dark */
[data-testid="stFileUploaderFile"] > div > div {
    background-color: #0f172a !important;
}

/* Text fix */
[data-testid="stFileUploaderFile"] span {
    color: white !important;
    font-weight: 500;
}

/* File size */
[data-testid="stFileUploaderFile"] small {
    color: rgba(255,255,255,0.6) !important;
}

/* Remove button */
[data-testid="stFileUploaderFile"] button {
    color: white !important;
    background: transparent !important;
}

/* Icon fix */
[data-testid="stFileUploaderFile"] svg {
    fill: white !important;
}

/* 🔥 Sticky Footer */
.footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background: linear-gradient(90deg, #020617, #0f172a);
    color: rgba(255,255,255,0.7);
    text-align: center;
    padding: 10px 0;
    font-size: 14px;
    border-top: 1px solid rgba(255,255,255,0.1);
    z-index: 100;
}

/* Prevent content overlap */
.main {
    padding-bottom: 60px;
}
<div class="footer">
    🚀 Built with Multi-Agent Intelligence | LangGraph Powered
</div>
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 🚀 Header
# -----------------------------
st.title("🚀 Autonomous Data Analytics Platform")

# spacing
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# glass card
st.markdown("""
<div class="card">
<h3>Enterprise Multi-Agent Analytics System</h3>

✔ Autonomous AI Agents  
✔ LangGraph Orchestration  
✔ Statistical Intelligence  
✔ Interactive Visualizations  
✔ Context-Aware Dataset Chat  
✔ Human-in-the-loop Approval  
✔ Business Intelligence Insights  

</div>
""", unsafe_allow_html=True)


# -----------------------------
# 🧠 Graph Init
# -----------------------------
graph = build_graph()

# -----------------------------
# 📂 Sidebar
# -----------------------------
state, page = render_sidebar()


if state:

    if page == "📊 Dashboard":
        render_dashboard(state, graph)

    elif page == "💬 Chat":
        render_chat(state)

