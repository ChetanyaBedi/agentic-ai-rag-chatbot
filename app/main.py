from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.graph import RAGGraph
from app.schemas import ChatRequest, ChatResponse, ContextChunk

app = FastAPI(
    title="Agentic AI eBook — RAG Chatbot",
    version="1.0.0",
    description="Strictly grounded RAG chatbot built with LangGraph, Pinecone and text embeddings.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = None


def get_rag() -> RAGGraph:
    global rag
    if rag is None:
        rag = RAGGraph()
    return rag


@app.get("/health")
def health():
    return {"status": "ok", "service": "agentic-ai-rag"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = get_rag().invoke(request.question)
    retrieved = result.get("retrieved", [])

    context = [
        ContextChunk(
            rank=i,
            page=int(item["page"]),
            score=round(float(item["score"]), 6),
            text=item["text"],
        )
        for i, item in enumerate(retrieved, start=1)
    ]

    return ChatResponse(
        answer=result.get("answer", ""),
        confidence_score=round(float(result.get("confidence_score", 0.0)), 6),
        retrieved_context=context,
        grounded=bool(result.get("grounded", False)),
    )
