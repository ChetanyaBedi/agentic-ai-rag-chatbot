from typing import List
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, description="Question about the Agentic AI eBook")


class ContextChunk(BaseModel):
    rank: int
    page: int
    score: float
    text: str


class ChatResponse(BaseModel):
    answer: str
    confidence_score: float
    retrieved_context: List[ContextChunk]
    grounded: bool
