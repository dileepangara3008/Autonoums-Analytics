import streamlit as st
import json


def render_insights(state):

    if not state.insights:
        st.info("No insights generated yet.")
        return

    st.markdown("## 💡 AI Insights")

    insights = state.insights

    # ======================================================
    # 🔥 SAFE PARSE
    # ======================================================
    if isinstance(insights, str):
        try:
            insights = json.loads(insights)
        except:
            st.info(insights)
            return

    if not isinstance(insights, dict):
        st.info(insights)
        return

    # helper
    def render_list(items, icon_fn):
        for item in items:
            if isinstance(item, str) and item.strip():
                icon_fn(item.strip())

    # ======================================================
    # 🔑 KEY INSIGHTS
    # ======================================================
    key_insights = insights.get("key_insights", [])
    if key_insights:
        st.markdown("### 🔑 Key Insights")
        render_list(key_insights, st.success)
    else:
        st.caption("No key insights available.")

    # ======================================================
    # 🔗 RELATIONSHIPS
    # ======================================================
    relationships = insights.get("relationships", [])
    if relationships:
        st.markdown("### 🔗 Relationships")
        render_list(relationships, st.info)
    else:
        st.caption("No relationships identified.")

    # ======================================================
    # ⚠️ ANOMALIES
    # ======================================================
    anomalies = insights.get("anomalies", [])
    if anomalies:
        st.markdown("### ⚠️ Anomalies")
        render_list(anomalies, st.warning)
    else:
        st.caption("No significant anomalies detected.")

    # ======================================================
    # 🚀 RECOMMENDATIONS
    # ======================================================
    recommendations = insights.get("recommendations", [])
    if recommendations:
        st.markdown("### 🚀 Recommendations")
        for rec in recommendations:
            if isinstance(rec, str) and rec.strip():
                st.markdown(f"• {rec.strip()}")
    else:
        st.caption("No recommendations generated.")