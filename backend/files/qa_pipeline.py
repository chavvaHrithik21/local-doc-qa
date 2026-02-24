import os
import tempfile
import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain_classic.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.llms import Ollama

persist_directory = "db"

def process_pdf(file_bytes):
    # Clear old DB first
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    loader = PyPDFLoader(tmp_path)
    pages = loader.load_and_split()

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(pages, embeddings, persist_directory=persist_directory)
    return True

def get_answer(query: str):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    retriever = vectorstore.as_retriever()

    # Pick a lighter Ollama model by default to reduce memory/CPU pressure.
    # Override via OLLAMA_MODEL env var if you install a different model.
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    local_llm = Ollama(model=ollama_model, temperature=0.7)
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=local_llm,
        retriever=retriever
    )

    return qa_chain.run(query)
