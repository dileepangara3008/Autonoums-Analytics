import streamlit as st

st.title("Autonomous Data Analytics AI")

file = st.file_uploader("Upload dataset")

if file:
    st.success("File uploaded")