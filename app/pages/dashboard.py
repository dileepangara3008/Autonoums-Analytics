import streamlit as st
import pandas as pd
import io

from app.components.hitl import handle_hitl
from app.components.metrics import render_metrics
from app.components.preview import render_preview
from app.components.eda_view import render_eda
from app.components.stats_view import render_stats
from app.components.charts_view import render_charts
from app.components.insights_view import render_insights


def render_dashboard(state, graph):

    df = state.cleaned_data if state.cleaned_data is not None else state.dataset

    st.subheader("📊 Dashboard")

    # 🔥 HITL
    state = handle_hitl(state, graph)

    # ======================================================
    # 📊 OVERVIEW
    # ======================================================
    if df is not None:
        render_metrics(df)
        render_preview(df)

    st.markdown("---")

    # ======================================================
    # 📊 EDA (TOP)
    # ======================================================
    render_eda(state)

    st.markdown("---")

    # ======================================================
    # 📈 STATS (SUMMARY + DETAILS INSIDE)
    # ======================================================
    render_stats(state)

    st.markdown("---")

    # ======================================================
    # 📊 VISUALIZATIONS
    # ======================================================
    render_charts(state)

    st.markdown("---")

    # ======================================================
    # 💡 INSIGHTS
    # ======================================================
    render_insights(state)

    # ======================================================
    # ❌ ERRORS
    # ======================================================
    if state.errors:
        st.error(state.errors)