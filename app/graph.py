from __future__ import annotations

from typing import Any, Dict, List, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph

from app.config import get_settings
from app.prompts import SYSTEM_PROMPT, USER_PROMPT
from app.vector_store import PineconeStore


class RAGState(TypedDict, total=False):
    question: str
    retrieved: List[Dict[str, Any]]
    answer: str
    confidence_score: float
    grounded: bool


def _format_context(chunks: List[Dict[str, Any]]) -> str:
    parts = []

    for item in chunks:
        parts.append(
            f"[Page {item['page']} | Retrieval score {item['score']:.4f}]\n"
            f"{item['text']}"
        )

    return "\n\n---\n\n".join(parts)


class RAGGraph:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.store = PineconeStore()

        # Local LLM. No OpenAI API key or API billing is required.
        self.llm = ChatOllama(
            model=self.settings.ollama_model,
            base_url=self.settings.ollama_base_url,
            temperature=0,
        )

        self.graph = self._build_graph()

    def retrieve_node(self, state: RAGState) -> RAGState:
        results = self.store.query(
            state["question"],
            top_k=self.settings.top_k,
        )

        results = [
            r
            for r in results
            if r["text"]
            and r["score"] >= self.settings.min_relevance_score
        ]

        confidence = max(
            (r["score"] for r in results),
            default=0.0,
        )

        return {
            "retrieved": results,
            "confidence_score": confidence,
        }

    def generate_node(self, state: RAGState) -> RAGState:
        chunks = state.get("retrieved", [])

        if not chunks:
            return {
                "answer": (
                    "I don't have enough information in the provided "
                    "eBook to answer that."
                ),
                "grounded": False,
            }

        context = _format_context(chunks)

        messages = [
            SystemMessage(
                content=SYSTEM_PROMPT.format(context=context)
            ),
            HumanMessage(
                content=USER_PROMPT.format(
                    question=state["question"]
                )
            ),
        ]

        response = self.llm.invoke(messages)
        answer = (
            response.content
            if isinstance(response.content, str)
            else str(response.content)
        )

        return {
            "answer": answer.strip(),
            "grounded": True,
        }

    def _build_graph(self):
        workflow = StateGraph(RAGState)

        workflow.add_node("retrieve", self.retrieve_node)
        workflow.add_node("generate", self.generate_node)

        workflow.add_edge(START, "retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)

        return workflow.compile()

    def invoke(self, question: str) -> Dict[str, Any]:
        return self.graph.invoke({"question": question})
