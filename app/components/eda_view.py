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
            # 🔥 FIX Arrow Serialization Issue (PROPER)
            # -----------------------------
            df_summary = df_summary.copy()

            for col in df_summary.columns:

                # try numeric conversion
                converted = pd.to_numeric(df_summary[col], errors="coerce")

                # if most values are numeric → keep numeric
                if converted.notna().sum() > 0:
                    df_summary[col] = converted

                else:
                    # otherwise convert to string
                    df_summary[col] = df_summary[col].astype(str)

            # replace NaN with None (safe)
            df_summary = df_summary.where(pd.notnull(df_summary), None)

    if "summary" in eda:
        st.success(eda["summary"])