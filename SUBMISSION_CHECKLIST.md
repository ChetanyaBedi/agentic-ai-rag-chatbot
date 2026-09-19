# Submission Checklist

## Local verification

- [ ] `.env` created from `.env.example`
- [ ] Pinecone key works
- [ ] Ollama installed
- [ ] Ollama model pulled successfully
- [ ] PDF placed in `data/Ebook-Agentic-AI.pdf`
- [ ] `python scripts/ingest.py --pdf data/Ebook-Agentic-AI.pdf`
- [ ] `uvicorn app.main:app --reload`
- [ ] `/docs` works
- [ ] 5–6 sample queries tested
- [ ] `pytest -q` passes

## GitHub

- [ ] `.env` is NOT committed
- [ ] API keys are NOT committed
- [ ] PDF is NOT committed unless you have permission to redistribute it
- [ ] README is present
- [ ] architecture explanation is present
- [ ] sample queries are present
- [ ] repository is public or accessible to reviewers

## Employer submission

- [ ] Reply to HR confirming assignment acceptance
- [ ] Submit GitHub repository link through the provided Google Form
- [ ] Share CV by email as requested
