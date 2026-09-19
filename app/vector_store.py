from __future__ import annotations

from typing import Any, Dict, List

from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone, ServerlessSpec

from app.config import get_settings


class PineconeStore:
    """Pinecone wrapper using a free local HuggingFace embedding model."""

    def __init__(self) -> None:
        self.settings = get_settings()

        # Runs locally. No OpenAI API call is made here.
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.settings.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        self.pc = Pinecone(api_key=self.settings.pinecone_api_key)
        self.index = self._get_or_create_index()

    def _get_or_create_index(self):
        name = self.settings.pinecone_index_name
        existing = {idx["name"] for idx in self.pc.list_indexes()}

        if name not in existing:
            self.pc.create_index(
                name=name,
                dimension=self.settings.embedding_dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=self.settings.pinecone_cloud,
                    region=self.settings.pinecone_region,
                ),
            )

        return self.pc.Index(name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.embeddings.embed_query(text)

    def upsert(
        self,
        records: List[Dict[str, Any]],
        namespace: str = "agentic-ai",
    ) -> None:
        self.index.upsert(vectors=records, namespace=namespace)

    def query(
        self,
        query: str,
        top_k: int,
        namespace: str = "agentic-ai",
    ) -> List[Dict[str, Any]]:
        vector = self.embed_query(query)

        result = self.index.query(
            namespace=namespace,
            vector=vector,
            top_k=top_k,
            include_metadata=True,
        )

        matches = getattr(result, "matches", None)
        if matches is None and isinstance(result, dict):
            matches = result.get("matches", [])
        matches = matches or []

        output = []
        for match in matches:
            metadata = getattr(match, "metadata", None)
            if metadata is None and isinstance(match, dict):
                metadata = match.get("metadata", {})

            score = getattr(match, "score", None)
            if score is None and isinstance(match, dict):
                score = match.get("score", 0.0)

            output.append(
                {
                    "id": (
                        getattr(match, "id", None)
                        if not isinstance(match, dict)
                        else match.get("id")
                    ),
                    "score": float(score or 0.0),
                    "page": int((metadata or {}).get("page", 0)),
                    "text": (metadata or {}).get("text", ""),
                    "source": (metadata or {}).get(
                        "source", "Agentic AI eBook"
                    ),
                    "chunk_id": (metadata or {}).get("chunk_id", ""),
                }
            )

        return output
