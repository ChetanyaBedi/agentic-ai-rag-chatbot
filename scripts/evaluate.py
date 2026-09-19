from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx

SAMPLE_QUERIES = [
    "What are the core pillars of an Agentic AI system?",
    "How are LLMs different from agents according to the eBook?",
    "What are the main categories of agentic systems?",
    "What are the challenges of multi-agent systems and their mitigation strategies?",
    "What are the four organizational readiness levels for Agentic AI?",
    "What practical Agentic AI use cases are described in the eBook?",
]


def main() -> None:
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

    results = []
    for question in SAMPLE_QUERIES:
        response = httpx.post(
            f"{base_url}/chat",
            json={"question": question},
            timeout=120,
        )
        response.raise_for_status()
        payload = response.json()
        results.append(
            {
                "question": question,
                "confidence_score": payload["confidence_score"],
                "grounded": payload["grounded"],
                "answer": payload["answer"],
                "pages": [c["page"] for c in payload["retrieved_context"]],
            }
        )

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
