import streamlit as st
from agents.chat_agent import run_chat_agent


def render_chat(state):

    st.subheader("💬 Chat with your Data")

    # ======================================================
    # 🧠 DISPLAY CHAT HISTORY
    # ======================================================
    if state.chat_history:

        for chat in state.chat_history[-5:]:

            # -----------------------------
            # USER MESSAGE
            # -----------------------------
            with st.chat_message("user"):
                st.write(chat["user"])

            # -----------------------------
            # ASSISTANT MESSAGE
            # -----------------------------
            with st.chat_message("assistant"):

                resp = chat["assistant"]

                # 🎯 HANDLE CHART RESPONSE
                if isinstance(resp, dict) and resp.get("type") == "chart":

                    fig = resp.get("figure")

                    if fig:
                        st.plotly_chart(fig, use_container_width=True)

                    if resp.get("text"):
                        st.write(resp["text"])

                else:
                    st.write(resp)

    # ======================================================
    # 💬 USER INPUT
    # ======================================================
    query = st.chat_input("Ask anything...")

    if query:

        # -----------------------------
        # SHOW USER MESSAGE
        # -----------------------------
        with st.chat_message("user"):
            st.write(query)

        # -----------------------------
        # GET RESPONSE
        # -----------------------------
        response = run_chat_agent(query, state)

        # -----------------------------
        # SHOW ASSISTANT RESPONSE
        # -----------------------------
        with st.chat_message("assistant"):

            # 🎯 HANDLE CHART RESPONSE
            if isinstance(response, dict) and response.get("type") == "chart":

                fig = response.get("figure")

                if fig:
                    st.plotly_chart(fig, use_container_width=True)

                if response.get("text"):
                    st.write(response["text"])

            else:
                st.write(response)

        # ======================================================
        # 💾 SAVE STATE
        # ======================================================
        st.session_state.state = state

        # 🔄 RERUN TO UPDATE CHAT
        st.rerun()