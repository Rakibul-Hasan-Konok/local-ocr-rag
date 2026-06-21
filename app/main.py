import os
import shutil
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel

from app.ocr import extract_text
from app.chunker import create_chunks
from app.vector_store import add_chunks, search_chunks
from app.rag import generate_answer

app = FastAPI(
    title="Local OCR & Dynamic RAG System",
    description="Fully local Bangla-English OCR + ChromaDB + Ollama RAG pipeline",
    version="1.0.0"
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class SearchRequest(BaseModel):
    query: str
    language: Optional[str] = None
    document_type: Optional[str] = None
    document_date: Optional[str] = None


@app.get("/")
def home():
    return {
        "message": "Local OCR & Dynamic RAG System is running",
        "docs": "http://127.0.0.1:8000/docs"
    }


@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    document_date: str = Form(...),
    language: str = Form(...)
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print("=" * 60)
    print(f"File uploaded: {file.filename}")
    print(f"Document type: {document_type}")
    print(f"Document date: {document_date}")
    print(f"Language: {language}")
    print("Starting local OCR/text extraction...")

    extracted_text = extract_text(file_path)

    print("Extraction completed.")
    print("Creating text chunks...")

    chunks = create_chunks(extracted_text)

    metadata = {
        "filename": file.filename,
        "document_type": document_type,
        "document_date": document_date,
        "language": language
    }

    total_chunks = add_chunks(chunks, metadata)

    print(f"Stored {total_chunks} chunks in ChromaDB.")
    print("=" * 60)

    return {
        "status": "success",
        "filename": file.filename,
        "document_type": document_type,
        "document_date": document_date,
        "language": language,
        "total_chunks": total_chunks,
        "sample_text": extracted_text[:1000]
    }


@app.post("/search")
def search_document(request: SearchRequest):
    filters = {
        "language": request.language,
        "document_type": request.document_type,
        "document_date": request.document_date
    }

    print("=" * 60)
    print(f"Query: {request.query}")
    print(f"Filters: {filters}")
    print("Searching filtered vector database...")

    results = search_chunks(
        query=request.query,
        filters=filters,
        top_k=10
    )

    contexts = results["documents"][0] if results.get("documents") else []
    metadatas = results["metadatas"][0] if results.get("metadatas") else []

    if not contexts:
        return {
            "query": request.query,
            "filters": filters,
            "answer": "No matching document chunks found for the given query and filters.",
            "sources": [],
            "retrieved_contexts": []
        }

    print(f"Retrieved {len(contexts)} chunks.")
    print("Generating local RAG answer using Ollama...")

    answer = generate_answer(request.query, contexts)

    print("Answer generated.")
    print("=" * 60)

    return {
        "query": request.query,
        "filters": filters,
        "answer": answer,
        "sources": metadatas,
        "retrieved_contexts": contexts
    }