# Agentic AI eBook — RAG Chatbot

A production-style AI Engineering Intern assignment implementation using **Python, LangGraph, Pinecone, local text embeddings, Ollama, FastAPI and Streamlit**.

This version is designed so that **OpenAI API billing is not required**.

## Architecture

```text
Agentic AI eBook PDF
        |
        v
     PyMuPDF
        |
        v
Page-aware text
        |
        v
Recursive chunking
        |
        v
Local HuggingFace Embeddings
all-MiniLM-L6-v2 (384 dimensions)
        |
        v
Pinecone
        |
        | user question
        v
     LangGraph
        |
        v
Retrieve Top-K chunks
        |
        v
Relevant chunks?
   |             |
  No            Yes
   |             |
Fallback       Ollama
                 |
                 v
             Final answer
                 |
                 v
Answer + retrieved context + score
                 |
            FastAPI / Streamlit
```

## 1. What this project does

The system:

1. Extracts text from the Agentic AI eBook using PyMuPDF.
2. Preserves PDF page numbers.
3. Splits the text into overlapping chunks.
4. Creates embeddings locally using `sentence-transformers/all-MiniLM-L6-v2`.
5. Stores the 384-dimensional vectors in Pinecone.
6. Uses LangGraph to orchestrate retrieval and generation.
7. Retrieves the most relevant chunks for a question.
8. Sends only those chunks to a local Ollama LLM.
9. Uses a strict prompt that tells the model to answer only from the retrieved eBook context.
10. Returns the answer, retrieved context, page numbers and similarity score.


