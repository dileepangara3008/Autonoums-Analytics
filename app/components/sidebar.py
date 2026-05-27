import streamlit as st
from core.state import AgentState
from agents.ingestion_agent import ingestion_agent


st.markdown("""
<style>

/* 🚫 Hide default uploaded file UI (SIDEBAR FIX) */
section[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] {
    display: none !important;
}

/* Also hide inner container just in case */
section[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] * {
    display: none !important;
}

</style>
""", unsafe_allow_html=True)

def render_sidebar():

    st.sidebar.title("📂 Controls")

    file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

    # -----------------------------
    # 🔥 CUSTOM DARK FILE DISPLAY
    # -----------------------------
    if file:
        st.sidebar.markdown(f"""
        <div style="
            background: #0f172a;
            padding: 12px;
            border-radius: 10px;
            margin-top: 10px;
        ">
            <div style="color:white; font-weight:500;">
                📄 {file.name}
            </div>
            <div style="color:rgba(255,255,255,0.6); font-size:12px;">
                {(file.size/1024):.1f} KB
            </div>
        </div>
        """, unsafe_allow_html=True)

    page = st.sidebar.radio("Navigate", ["📊 Dashboard", "💬 Chat"])

    if "state" not in st.session_state:
        st.session_state.state = None

    if file and st.sidebar.button("🚀 Start Pipeline"):

        state = AgentState()
        state.file = file

        with st.sidebar.spinner("🤖 Running agents..."):
            state = ingestion_agent(state)

        st.session_state.state = state
        st.rerun()

    return st.session_state.state, page