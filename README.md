# Local Document Q&A — PDF Question Answering with RAG

A **local-first Retrieval-Augmented Generation (RAG)** API that lets you upload a PDF and ask natural-language questions about its contents. The application extracts and chunks PDF text, generates semantic embeddings, stores them in a local Chroma vector database, retrieves relevant passages, and uses an Ollama-hosted language model to generate answers.

> **Project status:** Backend API prototype. It has interactive Swagger documentation, but no separate web chat frontend in the inspected implementation. Each new PDF upload replaces the previously indexed document.

## Tech stack

| Component | Technology | Purpose |
| --- | --- | --- |
| API | Python, FastAPI, Uvicorn | Upload and query endpoints |
| PDF ingestion | PyPDFLoader (`langchain-community`), PyPDF | Extract text from PDFs |
| Embeddings | Hugging Face Sentence Transformers, `all-MiniLM-L6-v2` | Convert text into vectors |
| Vector storage | Chroma (`langchain-chroma`) | Persist and retrieve document chunks locally |
| RAG orchestration | LangChain Classic `RetrievalQA` | Connect retrieval to generation |
| Local LLM | Ollama, `llama3.2:1b` | Generate answers from retrieved context |

## Architecture

```text
                     POST /upload (PDF)
                            |
                            v
                     FastAPI backend
                            |
                            v
                       PyPDFLoader
                            |
                            v
                     Text chunks/pages
                            |
                            v
           all-MiniLM-L6-v2 embedding model
                            |
                            v
                  Chroma local DB (db/)

                 POST /query (question)
                            |
                            v
                Embed question + retrieve
                  relevant Chroma chunks
                            |
                            v
               LangChain RetrievalQA chain
                            |
                            v
                Ollama (llama3.2:1b)
                            |
                            v
                       JSON answer
```

## Repository structure

```text
local-doc-qa/
├── README.md
├── LICENSE
└── backend/
    └── files/
        ├── main.py            # FastAPI app and endpoints
        ├── qa_pipeline.py     # PDF processing, embeddings, retrieval, LLM
        ├── requirements.txt   # Current dependency list (see note below)
        └── db/                # Created at runtime; local vector index
```

## Prerequisites

- Python 3.10+ (a recent compatible Python version is recommended).
- Git.
- [Ollama](https://ollama.com/download) installed locally and running.
- Internet access on first setup to download Python packages, the embedding model, and the Ollama model. After downloading these assets, inference is local.
- Sufficient RAM and disk space for the models.

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/chavvaHrithik21/local-doc-qa.git
cd local-doc-qa/backend/files
```

### 2. Create and activate a virtual environment

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

The repository's current `requirements.txt` is missing packages that `qa_pipeline.py` imports (`langchain-community`, `langchain-classic`, `langchain-huggingface`, and `langchain-chroma`). Install the existing requirements **and** these additional packages:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install langchain-community langchain-classic langchain-huggingface langchain-chroma
```

> **Recommended repository fix:** Add those four packages to `backend/files/requirements.txt`, then test a clean installation. LangChain integrations evolve rapidly, so pin tested compatible versions once you have a working environment. The current code also uses the older `langchain_community.llms.Ollama` integration, which may emit a deprecation warning.

### 4. Start Ollama and download the LLM

Install Ollama using the link above. Open the Ollama application, or start the service manually in a separate terminal if it is not already running:

```bash
ollama serve
```

In another terminal, download the model:

```bash
ollama pull llama3.2:1b
ollama list
```

If `ollama serve` reports that the address is already in use, the Ollama service may already be running; check with `ollama list`.

### 5. Start the FastAPI backend

From `local-doc-qa/backend/files` with the virtual environment activated:

```bash
python main.py
```

The default address is **http://localhost:8000**. Open **http://localhost:8000/docs** for interactive Swagger API documentation.

Alternatively:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 6. Upload a PDF

**Swagger UI:** Open `/docs` → expand `POST /upload` → **Try it out** → choose a PDF file → **Execute**.

**Terminal:**

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@/absolute/path/to/sample.pdf"
```

Expected success response:

```json
{"message": "Document processed successfully."}
```

The API extracts text, generates embeddings, and creates a local `db/` directory. Processing can take longer on the first run because the embedding model must download.

### 7. Ask questions about the PDF

**Swagger UI:** Expand `POST /query` → **Try it out** → enter a question in the `question` field → **Execute**.

**Terminal:**

```bash
curl -X POST "http://localhost:8000/query" \
  -F "question=What are the main findings of this document?"
```

Expected response shape (the actual answer depends on the uploaded PDF):

```json
{"answer": "The document discusses ..."}
```

**Important:** `/query` expects **form data**, not a JSON request body. Upload a PDF before asking questions.

## API reference

| Method | Endpoint | Request | Response |
| --- | --- | --- | --- |
| `GET` | `/` | None | Backend status message |
| `POST` | `/upload` | Multipart file field `file` containing a `.pdf` | Processing status or error |
| `POST` | `/query` | Form field `question` | Generated `answer` or error |

The current code returns error messages as JSON objects rather than consistently setting appropriate HTTP error status codes.

## Configuration

`main.py` loads environment variables from `.env` when present. Create an optional `.env` file inside `backend/files/`:

```dotenv
HOST=127.0.0.1
PORT=8000
RELOAD=false
OLLAMA_MODEL=llama3.2:1b
```

`OLLAMA_MODEL` selects the local Ollama model. Pull any alternative model before setting its name. No OpenAI API key is required for the current local inference pipeline.

## How retrieval-augmented generation works here

1. **Ingestion:** FastAPI reads the uploaded PDF bytes.
2. **Parsing and chunking:** `PyPDFLoader.load_and_split()` extracts the PDF into LangChain document chunks.
3. **Embedding:** `all-MiniLM-L6-v2` maps each chunk into a dense semantic vector.
4. **Indexing:** Chroma stores those vectors on disk in `db/`.
5. **Retrieval:** A user question is embedded, and Chroma retrieves relevant chunks.
6. **Generation:** LangChain passes retrieved context and the question to the Ollama model through `RetrievalQA`.
7. **Response:** The API returns the generated answer as JSON.

The model is **not fine-tuned** on the PDF; the PDF is used as retrieved context at query time.

## Limitations

- **Single active document:** `process_pdf()` deletes `db/` on each upload, replacing the previous index.
- **No source citations:** The query endpoint returns only the answer string, not page references or source documents.
- **Text-based PDF extraction:** Scanned or image-only PDFs may need OCR, which is not implemented.
- **No authentication or upload-size limit:** This is a local demo, not a hardened production service.
- **Broad CORS policy:** The API currently permits all origins.
- **Potential model hallucinations:** Retrieved context improves grounding but does not guarantee accuracy.
- **No frontend:** Interaction is via Swagger UI or an HTTP client.
- **Temporary files:** The PDF processing code creates a temporary file without deleting it afterward.

## Troubleshooting

**`ModuleNotFoundError: No module named 'langchain_community'` (or `langchain_classic`, `langchain_huggingface`, `langchain_chroma`)**

Install the four additional LangChain integration packages from step 3, ensuring the virtual environment is activated.

**`Connection refused` / Ollama unavailable**

Start Ollama, confirm the service is running, and verify that `ollama list` works. The application expects Ollama's default local endpoint.

**`model 'llama3.2:1b' not found`**

Run `ollama pull llama3.2:1b`, or set `OLLAMA_MODEL` to a model already installed locally.

**Query returns an empty or irrelevant answer**

Upload a text-based PDF first. Try a specific question supported by the document. Scanned PDFs without extractable text are not supported by the current pipeline.

**Port 8000 already in use**

Stop the existing server or set `PORT=8001` in `.env` and run `python main.py` again.

**Chroma / LangChain version conflicts**

Use a fresh virtual environment and install compatible versions. Record and pin the versions that work together; the existing requirements are not pinned.

## Suggested enhancements

- Support multiple PDFs and document IDs without deleting previous indexes.
- Return retrieved source snippets and PDF page citations.
- Add configurable chunk size, overlap, retrieval `k`, and model temperature.
- Improve file validation, error handling, and temporary-file cleanup.
- Add a simple Streamlit or React chat interface.
- Add unit/integration tests, dependency pinning, and Docker support.
- Introduce document-level access control before any shared deployment.

## License

MIT — see `LICENSE` in the repository.
