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

        # -----------------------------
        # 🧠 EXTRACT COLUMNS
        # -----------------------------
        x = plan.get("x")
        y = plan.get("y")
        col = plan.get("column")

        # detect types
        def is_categorical(c):
            return df[c].dtype == "object"

        def is_numeric(c):
            return df[c].dtype != "object"

        # -----------------------------
        # 📊 HISTOGRAM
        # -----------------------------
        if chart_type == "histogram" and col:
            return px.histogram(df, x=col, title=f"Distribution of {col}")

        # -----------------------------
        # 📊 SCATTER
        # -----------------------------
        if chart_type == "scatter" and x and y:
            return px.scatter(df, x=x, y=y,
                              title=f"{y} vs {x}")

        # -----------------------------
        # 📊 LINE
        # -----------------------------
        if chart_type == "line" and x and y:

            # if x categorical → aggregate
            if is_categorical(x) and is_numeric(y):
                df_grouped = df.groupby(x)[y].mean().reset_index()
                return px.line(df_grouped, x=x, y=y,
                               title=f"Average {y} by {x}")

            return px.line(df, x=x, y=y)

        # -----------------------------
        # 📊 BAR (MOST IMPORTANT)
        # -----------------------------
        if chart_type == "bar" and x:

            # case 1: categorical x + numeric y
            if x and y and is_categorical(x) and is_numeric(y):

                df_grouped = df.groupby(x)[y].sum().reset_index()

                return px.bar(
                    df_grouped,
                    x=x,
                    y=y,
                    title=f"Total {y} by {x}"
                )

            # case 2: only categorical x → count
            if x and is_categorical(x) and not y:

                df_grouped = df[x].value_counts().reset_index()
                df_grouped.columns = [x, "count"]

                return px.bar(
                    df_grouped,
                    x=x,
                    y="count",
                    title=f"Count of {x}"
                )

            # fallback
            if x and y:
                return px.bar(df, x=x, y=y)

        # -----------------------------
        # 📊 BOX
        # -----------------------------
        if chart_type == "box":

            if y:
                return px.box(df, y=y, title=f"Distribution of {y}")

            if col:
                return px.box(df, y=col)

        # -----------------------------
        # 📊 HEATMAP
        # -----------------------------
        if chart_type == "heatmap":

            numeric_df = df.select_dtypes(include="number")

            return px.imshow(
                numeric_df.corr(),
                text_auto=True,
                title="Correlation Heatmap"
            )

    except Exception as e:
        print("Chart error:", e)

    return None


@traceable(name="Chat Agent")
def run_chat_agent(query, state):

    llm = get_llm()

    df = state.cleaned_data if state.cleaned_data is not None else state.dataset

    # -----------------------------
    # 🧠 CONTEXT
    # -----------------------------
    history_text = ""

    for h in state.chat_history[-5:]:
        history_text += f"User: {h['user']}\nAssistant: {h['assistant']}\n"

    # -----------------------------
    # 🧠 CONTEXT RESOLUTION (NEW)
    # -----------------------------
    context_prompt = f"""
    You are a smart assistant.

    Conversation:
    {history_text}

    Current query:
    {query}

    Task:
    Rewrite the query to be fully explicit by resolving references like:
    - "they"
    - "it"
    - "them"

    Example:
    User: how many categories?
    User: what are they?
    → what are the categories

    Return ONLY rewritten query.
    """

    resolved_query = llm.invoke(context_prompt).content.strip()

    # -----------------------------
    # 🧠 STEP 1: DECIDE APPROACH (VERY IMPORTANT)
    # -----------------------------
    decision_prompt = f"""
    You are an intelligent data assistant.

    Your job is to decide HOW to answer the user query.

    Available approaches:
    1. DATA → requires dataframe operations (exact values, filtering, aggregation, listing values)
    2. VISUALIZATION → requires generating a chart
    3. INSIGHT → requires explanation using EDA/statistics/insights
    4. GENERAL → normal conversation

    DATASET COLUMNS:
    {df.columns.tolist()}

    EDA RESULTS:
    {state.eda_results}

    STATISTICAL RESULTS:
    {state.statistical_results}

    EXISTING INSIGHTS:
    {state.insights}

    QUERY:
    {resolved_query}

    RULES:
    - If query asks for values, counts, categories, listing → DATA
    - If query asks for chart/plot → VISUALIZATION
    - If query asks why/explain/reason → INSIGHT
    - If unclear → GENERAL

    Return ONLY ONE WORD:
    DATA / VISUALIZATION / INSIGHT / GENERAL
    """

    decision = llm.invoke(decision_prompt).content.strip().upper()

    try:

        # -----------------------------
        # 📊 DATA → PANDAS AGENT
        # -----------------------------
        if decision == "DATA":

            agent = create_pandas_dataframe_agent(
                llm,
                df,
                verbose=False,
                allow_dangerous_code=True
            )

            data_prompt = f"""
            You are a pandas dataframe expert.

            STRICT RULES:
            - Use ONLY the dataframe (df)
            - DO NOT assume anything
            - DO NOT invent values
            - Always compute using pandas

            SPECIAL:
            - For categories → use df[col].unique()
            - For counts → use value_counts()
            - For aggregation → use groupby()

            DATASET COLUMNS:
            {df.columns.tolist()}

            QUERY:
            {resolved_query}

            Return ONLY final answer.
            """

            result = agent.invoke(data_prompt)
            response = result.get("output", result)

        # -----------------------------
        # 📊 VISUALIZATION (KEEP YOUR LOGIC)
        # -----------------------------
        elif decision == "VISUALIZATION":

            plan = plan_chart_with_llm(query, df, state, llm)
            fig = generate_chart_from_plan(plan, df)

            response = {
                "type": "chart",
                "figure": fig,
                "text": f"Generated {plan.get('type')} chart."
            }

        # -----------------------------
        # 🧠 INSIGHT
        # -----------------------------
        elif decision == "INSIGHT":

            insight_prompt = f"""
            You are a senior data analyst.

            Use the following context to answer:

            EDA RESULTS:
            {state.eda_results}

            STATISTICAL RESULTS:
            {state.statistical_results}

            INSIGHTS:
            {state.insights}

            RULES:
            - DO NOT compute manually
            - DO NOT assume values
            - Explain based on existing analysis
            - Be concise and clear

            QUERY:
            {resolved_query}
            """

            response = llm.invoke(insight_prompt).content.strip()

        # -----------------------------
        # 💬 GENERAL
        # -----------------------------
        else:

            general_prompt = f"""
            You are a helpful assistant.

            Conversation:
            {history_text}

            QUERY:
            {resolved_query}

            Answer naturally.
            """

            response = llm.invoke(general_prompt).content.strip()

    except Exception as e:
        response = f"Error processing query: {str(e)}"

    # -----------------------------
    # 💾 SAVE MEMORY
    # -----------------------------
    state.chat_history.append({
        "user": resolved_query,
        "assistant": response
    })

    return response

