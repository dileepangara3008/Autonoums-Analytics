from tools.embedding import get_embeddings
from tools.vector_store import create_vector_store
from rag.chunking import dataframe_to_text

def retrieval_agent(state):
    try:
        df = state.cleaned_data

        docs = dataframe_to_text(df)

        embeddings = get_embeddings()
        vector_db = create_vector_store(docs, embeddings)

        results = vector_db.similarity_search(state.query, k=3)

        state.retrieved_docs = [doc.page_content for doc in results]

        # 🔥 HITL VALIDATION
        state.current_stage = "POST_RETRIEVAL"
        state.waiting_for_input = True

    except Exception as e:
        state.errors.append(str(e))

    return state