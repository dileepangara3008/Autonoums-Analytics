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

            # 🔥 FIX Arrow Serialization Issue
            df_summary = df_summary.copy()

            for col in df_summary.columns:
                try:
                    df_summary[col] = pd.to_numeric(df_summary[col])
                except:
                    pass

            df_summary = df_summary.where(pd.notnull(df_summary), None)

            st.dataframe(df_summary, use_container_width=True)

    if "summary" in eda:
        st.success(eda["summary"])