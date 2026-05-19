import streamlit as st

def render_charts(state):

    if not state.charts:
        return

    st.markdown("## 📊 Visualizations")

    cols = st.columns(2)

    for i, chart in enumerate(state.charts):

        if isinstance(chart, dict) and "figure" in chart:

            cols[i % 2].plotly_chart(
                chart["figure"],
                width="stretch"
            )