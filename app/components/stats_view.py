import streamlit as st
import pandas as pd
import json

def render_stats(state):

    if not state.statistical_results:
        return

    st.markdown("## 📈 Statistical Analysis")

    stats_data = state.statistical_results

    # -----------------------------
    # 🧠 SUMMARY FIRST (IMPORTANT)
    # -----------------------------
    if isinstance(stats_data, dict) and stats_data.get("summary"):
        st.markdown("### 🧠 Key Takeaways")
        st.success(stats_data["summary"])

        st.markdown("---")

    # -----------------------------
    # 📊 DETAILED RESULTS
    # -----------------------------
    if "results" in stats_data:
        stats = stats_data["results"]
    else:
        stats = stats_data

    for key, value in stats.items():

        st.markdown(f"### 🔹 {key.replace('_',' ').title()}")

        import json

        if isinstance(value, str):
            try:
                value = json.loads(value)
            except:
                st.info(value)
                continue

        if isinstance(value, dict):

            if value.get("type") == "correlation":
                st.success(
                    f"{value['col1']} vs {value['col2']} → "
                    f"{round(value['correlation'],2)} (p={round(value['p_value'],3)})"
                )

            elif value.get("type") == "regression":
                st.success(
                    f"{value['feature']} → {value['target']} "
                    f"(R²={round(value['r2'],2)})"
                )

            elif value.get("type") == "anomaly":
                st.warning(f"{value['count']} anomalies in {value['column']}")

            elif value.get("type") == "distribution":
                st.info(
                    f"{value['column']} → Mean: {round(value['mean'],2)}, "
                    f"Std: {round(value['std'],2)}"
                )

            elif value.get("type") == "t_test":
                if value["significant"]:
                    st.success("Statistically significant difference")
                else:
                    st.info("No significant difference")

            elif "error" in value:
                st.error(value["error"])

        st.markdown("---")