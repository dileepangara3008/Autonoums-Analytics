import streamlit as st
import json


def render_insights(state):

    if not state.insights:
        return

    st.markdown("## 💡 AI Insights")

    insights = state.insights

    # ======================================================
    # 🔥 STEP 1: ALWAYS CONVERT TO DICT
    # ======================================================
    if isinstance(insights, str):
        try:
            insights = json.loads(insights)
        except:
            st.info(insights)  # fallback (rare)
            return

    if not isinstance(insights, dict):
        st.info(insights)
        return

    # ======================================================
    # 🔑 KEY INSIGHTS
    # ======================================================
    if insights.get("key_insights"):
        st.markdown("### 🔑 Key Insights")

        for insight in insights["key_insights"]:
            st.success(insight)

    # ======================================================
    # 🔗 RELATIONSHIPS
    # ======================================================
    if insights.get("relationships"):
        st.markdown("### 🔗 Relationships")

        for rel in insights["relationships"]:
            st.info(rel)

    # ======================================================
    # ⚠️ ANOMALIES
    # ======================================================
    if insights.get("anomalies"):
        st.markdown("### ⚠️ Anomalies")

        for anomaly in insights["anomalies"]:
            st.warning(anomaly)

    # ======================================================
    # 🚀 RECOMMENDATIONS
    # ======================================================
    if insights.get("recommendations"):
        st.markdown("### 🚀 Recommendations")

        for rec in insights["recommendations"]:
            st.markdown(f"- {rec}")