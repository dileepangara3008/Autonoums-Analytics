from core.config import get_llm
from langchain_experimental.agents import create_pandas_dataframe_agent
import json
import re
import plotly.express as px
from langsmith import traceable

def extract_json(text):
    try:
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return json.loads(text)
    except:
        return {}

def detect_query_type(query):

    q = query.lower()

    viz_keywords = [
        "plot", "chart", "graph", "visualize",
        "trend", "distribution"
    ]

    data_keywords = [
        "average", "mean", "sum", "total",
        "count", "max", "min",
        "top", "highest", "lowest",
        "calculate", "compute",
        "how many", "how much",
        "compare", "group by", "per", "by"
    ]

    insight_keywords = [
        "why", "reason", "insight", "explain"
    ]

    if any(word in q for word in viz_keywords):
        return "viz"

    if any(word in q for word in data_keywords):
        return "data"

    if any(word in q for word in insight_keywords):
        return "insight"

    return "general"

def plan_chart_with_llm(query, df, state, llm):

    prompt = f"""
    You are a data visualization expert.

    Dataset columns:
    {df.columns.tolist()}

    Numeric columns:
    {df.select_dtypes(include="number").columns.tolist()}

    Categorical columns:
    {df.select_dtypes(include="object").columns.tolist()}

    EDA Results:
    {state.eda_results}

    Statistical Results:
    {state.statistical_results}

    User Query:
    {query}

    Your task:
    Decide the BEST chart to answer the query.

    Chart types:
    - histogram
    - scatter
    - line
    - bar
    - box
    - heatmap

    Rules:
    - Choose relevant columns
    - Do NOT invent column names
    - Avoid id/index columns
    - Prefer meaningful relationships

    Return STRICT JSON:

    {{
      "type": "scatter",
      "x": "col1",
      "y": "col2"
    }}
    """

    decision = llm.invoke(prompt).content.strip()

    return extract_json(decision)

def generate_chart_from_plan(plan, df):

    try:
        chart_type = plan.get("type")

        if chart_type == "histogram":
            return px.histogram(df, x=plan["column"])

        if chart_type == "scatter":
            return px.scatter(df, x=plan["x"], y=plan["y"])

        if chart_type == "line":
            return px.line(df, x=plan["x"], y=plan["y"])

        if chart_type == "bar":
            return px.bar(df, x=plan["x"], y=plan["y"])

        if chart_type == "box":
            return px.box(df, y=plan["column"])

        if chart_type == "heatmap":
            numeric_df = df.select_dtypes(include="number")
            return px.imshow(numeric_df.corr())

    except Exception as e:
        print("Chart error:", e)

    return None


@traceable(name="Chat Agent")
def run_chat_agent(query, state):

    llm = get_llm()

    df = state.cleaned_data if state.cleaned_data is not None else state.dataset

    # -----------------------------
    # 🧠 HISTORY
    # -----------------------------
    history_text = ""

    for h in state.chat_history[-5:]:
        history_text += f"User: {h['user']}\nAssistant: {h['assistant']}\n"

    # -----------------------------
    # 🔀 ROUTER
    # -----------------------------
    qtype = detect_query_type(query)

    try:

        # -----------------------------
        # 📊 DATA QUERY → PANDAS AGENT
        # -----------------------------
        if qtype == "data":

            agent = create_pandas_dataframe_agent(
                llm,
                df,
                verbose=False,
                allow_dangerous_code=True
            )

            enhanced_query = f"""
            You are working with a pandas dataframe.

            IMPORTANT:
            - Use actual data
            - Do NOT assume anything
            - For comparisons, use groupby operations
            - Return exact results

            Examples:
            - "compare sales by region" → group by region and sum sales
            - "average sales by region" → group by region and mean

            Dataset columns:
            {df.columns.tolist()}

            Question:
            {query}
            """

            result = agent.invoke(enhanced_query)

            response = result.get("output", result)

        elif qtype == "viz":

            plan = plan_chart_with_llm(query, df, state, llm)

            fig = generate_chart_from_plan(plan, df)

            response = {
                "type": "chart",
                "figure": fig,
                "text": f"Generated {plan.get('type')} chart based on your query."
            }

        # -----------------------------
        # 🧠 INSIGHT QUERY → LLM
        # -----------------------------
        else:

            prompt = f"""
            You are a data analyst assistant.

            IMPORTANT RULE:
            - DO NOT perform calculations manually
            - If numerical calculation is needed, assume it is already computed
            - Only explain results

            Conversation History:
            {history_text}

            Dataset columns:
            {df.columns.tolist()}

            EDA Results:
            {state.eda_results}

            Statistical Results:
            {state.statistical_results}

            Insights:
            {state.insights}

            Question:
            {query}

            Answer clearly using context.
            """

            response = llm.invoke(prompt).content.strip()

    except Exception as e:
        response = f"Error processing query: {str(e)}"

    # -----------------------------
    # 💾 SAVE MEMORY
    # -----------------------------
    state.chat_history.append({
        "user": query,
        "assistant": response
    })

    return response

