# local-doc-qa

Local-first PDF question answering with FastAPI, LangChain, Chroma, sentence-transformers, and Ollama.

## Stack

- FastAPI for API endpoints
- LangChain + Chroma for retrieval
- `all-MiniLM-L6-v2` embeddings via `sentence-transformers`
- Ollama for local LLM inference (default: `llama3.2:1b`)

## API Endpoints

- `GET /` health message
- `POST /upload` upload a PDF and build a fresh index
- `POST /query` submit a question and get an answer from the indexed document

## How it works

1. Upload a PDF to `/upload`.
2. The file is parsed with `PyPDFLoader` and split into chunks.
3. Chunks are embedded and stored in local Chroma DB (`backend/files/db`).
4. Ask questions on `/query`; retrieved chunks are passed to Ollama through a RetrievalQA chain.

Note: each new upload clears and rebuilds the local vector DB.

## Run locally

```bash
cd backend/files
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama pull llama3.2:1b
python main.py
```

