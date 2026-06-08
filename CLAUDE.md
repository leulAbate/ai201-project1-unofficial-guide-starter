# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a CodePath AI201 course project: a RAG (Retrieval-Augmented Generation) pipeline called "The Unofficial Guide." The system ingests a corpus of documents on a chosen domain, chunks and embeds them into a vector store, then answers user queries by retrieving relevant chunks and grounding a Groq-hosted LLM on them.

## Setup

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Then edit .env and set GROQ_API_KEY=<your key>
```

If documents include PDFs, uncomment `pdfplumber==0.11.4` in `requirements.txt` before installing.  
If the query interface uses Gradio or Streamlit, uncomment the relevant line in `requirements.txt`.

## Running the Pipeline

No entry-point scripts exist yet — they are to be implemented. The expected pipeline stages and their likely script names (following the milestone structure in `planning.md`) are:

| Stage | What it does |
|-------|-------------|
| Ingestion | Loads raw files from `documents/` |
| Chunking | Splits documents into chunks (size + overlap TBD in `planning.md`) |
| Embedding + Vector Store | Encodes chunks with `sentence-transformers`, stores in ChromaDB |
| Retrieval | Queries ChromaDB for top-k chunks matching a user question |
| Generation | Sends retrieved chunks + query to Groq LLM; returns grounded answer |

## Tech Stack

- **Embeddings:** `sentence-transformers` (model chosen in `planning.md`)
- **Vector store:** `chromadb` (local, persistent)
- **LLM:** `groq` Python SDK — model served via Groq API (key in `.env`)
- **UI (optional):** Gradio or Streamlit
- **PDF parsing (optional):** `pdfplumber`
- **Config:** `python-dotenv` — always load `.env` before accessing `GROQ_API_KEY`

## Key Files

- `planning.md` — spec document (domain, chunking strategy, embedding model, evaluation plan, architecture diagram). Fill this in before writing pipeline code.
- `README.md` — submission report. Fill in each section after implementing the corresponding stage.
- `documents/` — place raw source documents here before running ingestion.
- `.env` — holds `GROQ_API_KEY`; never commit this file (already in `.gitignore`).

## Grounding Constraint

The LLM **must** be constrained to answer only from retrieved chunks. The system prompt must explicitly prohibit the model from drawing on outside knowledge. Retrieved chunk text should be formatted clearly in the prompt so the model can cite sources; low-relevance chunks should be filtered before passing to generation.
