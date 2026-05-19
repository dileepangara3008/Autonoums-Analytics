import streamlit as st
from agents.chat_agent import run_chat_agent

def render_chat(state):

    st.subheader("💬 Chat with your Data")

    if state.chat_history:

        for chat in state.chat_history[-5:]:

            with st.chat_message("user"):
                st.write(chat["user"])

            with st.chat_message("assistant"):
                st.write(chat["assistant"])

    query = st.chat_input("Ask anything...")

    if query:

        with st.chat_message("user"):
            st.write(query)

        response = run_chat_agent(query, state)

        with st.chat_message("assistant"):
            st.write(response)

        st.session_state.state = state
        st.rerun()