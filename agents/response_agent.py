from langchain_groq import ChatGroq
from core.config import GROQ_API_KEY

def response_agent(state):
    try:
        context = "\n".join(state.retrieved_docs)

        prompt = f"""
        Answer the question using ONLY this data:
        {context}

        Question:
        {state.query}
        """

        llm = ChatGroq(
                model="llama-3.1-8b-instant",
                temperature=0,
                api_key=GROQ_API_KEY
        )        
        response = llm.invoke(prompt)

        state.final_response = response.content
        state.current_stage = "DONE"

    except Exception as e:
        state.errors.append(str(e))

    return state