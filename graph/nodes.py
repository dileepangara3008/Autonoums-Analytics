from agents.ingestion_agent import ingestion_agent
from agents.eda_agent import run_eda_agent
from agents.stats_agent import run_stats_agent
from agents.viz_agent import run_viz_agent
from agents.insights_agent import run_insights_agent


# -----------------------------
# 📥 INGESTION
# -----------------------------
def ingestion_node(state):
    return ingestion_agent(state)


# -----------------------------
# 🔴 HITL NODE
# -----------------------------
def hitl_node(state):

    # 🔥 STOP EXECUTION HERE if HITL needed
    if state.waiting_for_input:
        return state

    return state


# -----------------------------
# 🔍 EDA
# -----------------------------
def eda_node(state):

    df = state.cleaned_data if state.cleaned_data is not None else state.dataset

    results = run_eda_agent(df)

    state.eda_results = results

    # 🔥 IMPORTANT: move pipeline forward
    state.current_stage = "EDA_DONE"

    return state


# -----------------------------
# 📊 STATS
# -----------------------------
def stats_node(state):

    df = state.cleaned_data if state.cleaned_data is not None else state.dataset

    results = run_stats_agent(df)

    state.statistical_results = results

    # 🔥 MOVE PIPELINE FORWARD
    state.current_stage = "STATS_DONE"

    return state


# -----------------------------
# 📈 VIZ
# -----------------------------
def viz_node(state):

    df = state.cleaned_data if state.cleaned_data is not None else state.dataset

    charts = run_viz_agent(df)

    state.charts = charts

    state.current_stage = "VIZ_DONE"

    return state


# -----------------------------
# 💡 INSIGHTS
# -----------------------------
def insights_node(state):

    df = state.cleaned_data if state.cleaned_data is not None else state.dataset

    insights = run_insights_agent(
        df,
        state.eda_results,
        state.statistical_results
    )

    state.insights = insights

    state.current_stage = "__end__"

    return state


# -----------------------------
# 🧠 PANDAS
# -----------------------------
def pandas_node(state):
    df = state.cleaned_data if state.cleaned_data is not None else state.dataset
    state.insights = run_pandas_agent(df, state.query)
    return state


# -----------------------------
# 🔗 NODE MAP
# -----------------------------
nodes = {
    "INGESTION": ingestion_node,
    "EDA": eda_node,
    "STATS": stats_node,
    "VIZ": viz_node,
    "INSIGHTS": insights_node,
}