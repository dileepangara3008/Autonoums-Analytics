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
        # GET RESPONSE (ONLY ONCE)
        # -----------------------------
        result = run_chat_agent(query, state, stream=True)

        # -----------------------------
        # SHOW ASSISTANT RESPONSE
        # -----------------------------
        with st.chat_message("assistant"):

            # ==========================================
            # 📊 HANDLE CHART RESPONSE
            # ==========================================
            if isinstance(result, dict) and result.get("type") == "chart":

                fig = result.get("figure")

                if fig:
                    st.plotly_chart(fig, use_container_width=True)

                if result.get("text"):
                    st.write(result["text"])

                full_response = result  # save as dict

            # ==========================================
            # 🔥 STREAM TEXT RESPONSE
            # ==========================================
            elif hasattr(result, "__iter__"):

                response_placeholder = st.empty()
                full_response = ""

                for chunk in result:
                    content = chunk.content if hasattr(chunk, "content") else str(chunk)
                    full_response += content

                    response_placeholder.markdown(full_response)

            # ==========================================
            # 💬 NORMAL RESPONSE (FALLBACK)
            # ==========================================
            else:
                st.write(result)
                full_response = result


        # -----------------------------
        # SAVE TO CHAT HISTORY
        # -----------------------------
        state.chat_history.append({
            "user": query,
            "assistant": full_response
        })