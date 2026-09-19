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

## 2. Important: no OpenAI API required

The previous version used OpenAI embeddings and an OpenAI chat model. That requires API credits.

This version replaces both:

| Component | Previous | Current |
|---|---|---|
| Embeddings | OpenAI | HuggingFace local |
| Embedding model | text-embedding-3-small | all-MiniLM-L6-v2 |
| Dimensions | 1536 | 384 |
| Generation | OpenAI | Ollama local |
| API billing | Required | Not required |

Pinecone is still used as the vector database. If your Pinecone account does not allow the required index on its current plan, the vector layer can be switched to another vector database without changing the LangGraph design.

## 3. Prerequisites

- Python 3.11 or 3.12
- Git
- Pinecone API key
- Ollama installed locally
- Internet connection for Python packages and the first HuggingFace model download

## 4. Windows setup

Open PowerShell inside the project folder.

### Create virtual environment

```powershell
python -m venv venv
```

Activate:

```powershell
venv\Scriptsctivate
```

### Install packages

```powershell
pip install -r requirements.txt
```

The first installation of `sentence-transformers` can take some time because it installs the local ML runtime.

## 5. Install Ollama

Install Ollama for Windows from the official Ollama website.

After installation, verify:

```powershell
ollama --version
```

Pull the configured local model:

```powershell
ollama pull llama3.2:3b
```

Test it:

```powershell
ollama run llama3.2:3b
```

Type a short question. Press Ctrl+C to exit.

Keep Ollama available while running the FastAPI chatbot.

## 6. Configure `.env`

Copy:

```powershell
copy .env.example .env
```

Open `.env`.

Add your Pinecone API key:

```env
PINECONE_API_KEY=your_pinecone_api_key
```

The important settings are:

```env
PINECONE_INDEX_NAME=agentic-ai-ebook-free

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

There is **no `OPENAI_API_KEY`** in this version.

## 7. Pinecone index

The local embedding model produces **384-dimensional vectors**.

Therefore, do not reuse a Pinecone index that was created for the old OpenAI 1536-dimensional embeddings.

Use:

```text
Index name: agentic-ai-ebook-free
Dimension: 384
Metric: cosine
```

The ingestion code can create the index automatically if the name does not already exist.

## 8. Add the eBook

Place the assigned PDF here:

```text
data/Ebook-Agentic-AI.pdf
```

The PDF is intentionally not committed to GitHub.

## 9. Ingest the PDF

Run:

```powershell
python scripts/ingest.py --pdf data/Ebook-Agentic-AI.pdf
```

The first run downloads the local embedding model.

Expected flow:

```text
PDF
 ↓
Text extraction
 ↓
Chunking
 ↓
Local embeddings
 ↓
Pinecone upsert
```

Expected final output:

```text
Ingestion complete.
Pages with text: ...
Chunks indexed: ...
Pinecone index: agentic-ai-ebook-free
Namespace: agentic-ai
```

## 10. Start FastAPI

```powershell
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000/docs
```

Health:

```text
http://localhost:8000/health
```

Chat endpoint:

```text
POST /chat
```

Example:

```json
{
  "question": "What are the core pillars of an Agentic AI system?"
}
```

Response contains:

```json
{
  "answer": "...",
  "confidence_score": 0.84,
  "retrieved_context": [
    {
      "rank": 1,
      "page": 19,
      "score": 0.84,
      "text": "..."
    }
  ],
  "grounded": true
}
```

The confidence score is the highest accepted Pinecone retrieval similarity score. It is **not a calibrated probability of correctness**.

## 11. Run Streamlit

Keep FastAPI running.

Open another PowerShell:

```powershell
venv\Scriptsctivate
streamlit run streamlit_app.py
```

Open:

```text
http://localhost:8501
```

## 12. Sample questions

1. What are the core pillars of an Agentic AI system?
2. How are LLMs different from agents according to the eBook?
3. What are the main categories of agentic systems?
4. What are the challenges of multi-agent systems and their mitigation strategies?
5. What are the four organizational readiness levels for Agentic AI?
6. What practical Agentic AI use cases are described in the eBook?

## 13. Run tests

```powershell
pytest -q
```

The API contract tests do not require a live LLM call.

For an end-to-end evaluation:

```powershell
python scripts/evaluate.py
```

Make sure FastAPI, Pinecone and Ollama are running/configured first.

## 14. Grounding strategy

The assignment requires the chatbot to stay grounded in the supplied eBook.

This implementation uses:

- Page-aware PDF extraction.
- Chunk-level retrieval.
- Pinecone similarity search.
- A configurable relevance threshold.
- A strict system prompt.
- A fallback when no relevant context is found.
- Local LLM generation using only retrieved context.
- Returned context chunks and page numbers for inspection.

## 15. Project structure

```text
agentic-ai-rag-chatbot/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── graph.py
│   ├── main.py
│   ├── prompts.py
│   ├── schemas.py
│   └── vector_store.py
│
├── scripts/
│   ├── __init__.py
│   ├── download_pdf.py
│   ├── evaluate.py
│   └── ingest.py
│
├── tests/
│   ├── __init__.py
│   └── test_api.py
│
├── data/
│   └── .gitkeep
│
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── streamlit_app.py
└── README.md
```

## 16. Interview explanation

> "I implemented a grounded RAG chatbot over the Agentic AI eBook. PyMuPDF extracts the PDF page by page, and the text is split into overlapping chunks while retaining page metadata. I generate 384-dimensional embeddings locally using the all-MiniLM-L6-v2 sentence-transformer and store them in Pinecone. LangGraph orchestrates a retrieval node followed by a generation node. At query time, the question is embedded locally, the top relevant chunks are retrieved, and only those chunks are passed to a local Ollama LLM through a strict grounding prompt. The API returns the answer along with retrieved context, page numbers and similarity score for traceability."

## 17. Key design decisions

### Chunking

```env
CHUNK_SIZE=900
CHUNK_OVERLAP=150
```

### Retrieval

```env
TOP_K=5
MIN_RELEVANCE_SCORE=0.25
```

### Embedding

```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
```

### Generation

```env
OLLAMA_MODEL=llama3.2:3b
```

Temperature is set to `0`.

## 18. GitHub security

Never commit:

```text
.env
PINECONE_API_KEY
```

Check before pushing:

```powershell
git status
git check-ignore -v .env
```

The assignment PDF should also remain local unless redistribution is explicitly permitted.

## 19. Docker note

The normal Windows setup is recommended for this assignment because Ollama runs as a local service.

If Docker is used, the container must be able to reach the host Ollama service. Do not assume `localhost:11434` inside a Linux container means the Windows host.

## 20. Future improvements

- Query rewriting.
- Reranking.
- Hybrid search.
- Answer verification node.
- Exact source citations.
- Evaluation dataset.
- Authentication and rate limiting.
- Observability and tracing.
