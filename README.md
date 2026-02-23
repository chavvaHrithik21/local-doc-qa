# llm-doc-qa
# LLM Document Q&A System

Local-first PDF question answering built with:

- `FastAPI` for the HTTP API
- `LangChain Classic` + `Chroma` for retrieval
- `sentence-transformers` (`all-MiniLM-L6-v2`) for embeddings
- `Ollama` for running a small on-device LLM (default `llama3.2:1b`)

## How it works

1. **Upload (`POST /upload`)**
   - The PDF is written to a temp file, parsed with `PyPDFLoader`, then chunked into pages.
   - Each chunk becomes an embedding vector via `HuggingFaceEmbeddings`.
   - Vectors are stored in a persistent Chroma DB located at `CHROMA_PERSIST_DIR` (defaults to your OS temp directory).
   - Any previous index is cleared so every upload resets the knowledge base.

2. **Query (`POST /query`)**
   - Incoming questions are embedded with the same encoder and passed to Chroma’s retriever.
   - Retrieved context chunks feed a LangChain `RetrievalQA` chain powered by an Ollama LLM.
   - The LLM temperature defaults to `0.7`; you can override the model by exporting `OLLAMA_MODEL`.

## Getting started

```bash
cd backend/venv
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
ollama pull llama3.2:1b  # or another local model
python main.py
```

Environment tweaks:

- `OLLAMA_MODEL`: pick another local model (e.g., `mistral`, `phi3.5:mini`).
- `CHROMA_PERSIST_DIR`: point to a writable folder if you want to keep embeddings between runs.
- `HOST`, `PORT`, `RELOAD`: FastAPI/Uvicorn settings used in `main.py`.

## Features

- Upload and index PDFs via REST
- Ask natural-language questions without cloud APIs
- Fully local pipeline (LLM + embeddings) once the models are downloaded
- Easy model/embedding swaps via environment variables


