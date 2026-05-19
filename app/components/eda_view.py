import streamlit as st
import pandas as pd
import json


def render_eda(state):

    if not state.eda_results:
        return

    st.markdown("## 📊 Exploratory Data Analysis")

    eda = state.eda_results

    if isinstance(eda, dict) and "raw_results" in eda:

        stats = eda["raw_results"].get("descriptive_statistics")

        if isinstance(stats, str):
            stats = json.loads(stats)

        if isinstance(stats, dict) and "summary" in stats:

            df_summary = pd.DataFrame(stats["summary"]).T

            # -----------------------------
            # ✅ FIX ARROW ISSUE
            # -----------------------------
            df_summary = df_summary.applymap(
                lambda x: float(x) if isinstance(x, (int, float)) else str(x)
            )
            st.dataframe(df_summary, width="stretch")

    if "summary" in eda:
        st.success(eda["summary"])