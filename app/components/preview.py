import streamlit as st

def render_preview(df):

    st.markdown("## 📂 Dataset Preview")

    st.dataframe(df.head(), width="stretch")