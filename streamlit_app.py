import requests
import streamlit as st

st.set_page_config(
    page_title="Agentic AI eBook RAG",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Agentic AI eBook — RAG Chatbot")
st.caption("Answers are grounded only in the provided Agentic AI eBook.")

api_url = st.sidebar.text_input("FastAPI URL", "http://localhost:8000")

question = st.text_input(
    "Ask a question",
    placeholder="e.g. What are the four organizational readiness levels?",
)

if st.button("Ask", type="primary") and question.strip():
    with st.spinner("Retrieving and generating..."):
        response = requests.post(
            f"{api_url}/chat",
            json={"question": question},
            timeout=120,
        )

    if response.ok:
        data = response.json()
        st.subheader("Answer")
        st.write(data["answer"])

        st.metric("Retrieval score", f"{data['confidence_score']:.4f}")
        st.write(f"Grounded: **{data['grounded']}**")

        st.subheader("Retrieved context")
        for item in data["retrieved_context"]:
            with st.expander(
                f"Rank {item['rank']} · Page {item['page']} · Score {item['score']:.4f}"
            ):
                st.write(item["text"])
    else:
        st.error(f"API error: {response.status_code} — {response.text}")
