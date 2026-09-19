from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

import fitz  # PyMuPDF
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Allow "python scripts/ingest.py" from repo root.
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.config import get_settings
from app.vector_store import PineconeStore


def load_pdf(pdf_path: str) -> list[Document]:
    pdf = fitz.open(pdf_path)
    documents = []

    for page_number, page in enumerate(pdf, start=1):
        text = page.get_text("text").strip()
        if not text:
            continue

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "page": page_number,
                    "source": Path(pdf_path).name,
                },
            )
        )

    pdf.close()
    return documents


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest the Agentic AI eBook into Pinecone.")
    parser.add_argument(
        "--pdf",
        default="data/Ebook-Agentic-AI.pdf",
        help="Path to the Agentic AI eBook PDF",
    )
    args = parser.parse_args()

    if not os.path.exists(args.pdf):
        raise FileNotFoundError(
            f"PDF not found: {args.pdf}\n"
            "Download the assigned eBook and place it at data/Ebook-Agentic-AI.pdf."
        )

    settings = get_settings()
    store = PineconeStore()

    documents = load_pdf(args.pdf)
    if not documents:
        raise RuntimeError("No extractable text was found in the PDF.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    texts = [doc.page_content for doc in chunks]
    embeddings = store.embed_documents(texts)

    records = []
    for i, (doc, vector) in enumerate(zip(chunks, embeddings)):
        page = int(doc.metadata.get("page", 0))
        chunk_id = hashlib.sha1(
            f"{doc.metadata.get('source')}|{page}|{i}|{doc.page_content}".encode("utf-8")
        ).hexdigest()

        records.append(
            {
                "id": chunk_id,
                "values": vector,
                "metadata": {
                    "text": doc.page_content,
                    "page": page,
                    "source": doc.metadata.get("source", "Agentic AI eBook"),
                    "chunk_id": chunk_id,
                },
            }
        )

    batch_size = 100
    for start in range(0, len(records), batch_size):
        batch = records[start:start + batch_size]
        store.upsert(batch)
        print(f"Upserted {min(start + batch_size, len(records))}/{len(records)} chunks")

    print("\nIngestion complete.")
    print(f"Pages with text: {len(documents)}")
    print(f"Chunks indexed: {len(records)}")
    print(f"Pinecone index: {settings.pinecone_index_name}")
    print("Namespace: agentic-ai")


if __name__ == "__main__":
    main()
