import os
from typing import List

from app.db.session import get_db
from app.services.rag_service import delete_all_files, query_rag, save_uploaded_file
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from llama_index.core import SimpleDirectoryReader
from sqlalchemy.orm import Session

load_dotenv()

router = APIRouter()

DATA_PATH = os.getenv("DATA_PATH")


@router.post("/upload_file/")
async def upload_file(
    files: List[UploadFile] = File(...), db: Session = Depends(get_db)
):
    """
    Upload one or multiple files and store metadata in the database.
    """
    upload_files = []
    for file in files:
        result = save_uploaded_file(file, db)
        if result is None:
            raise HTTPException(
                status_code=400, detail=f"File {file.filename} already exists"
            )
        upload_files.append(result)
    return {"upload_files": upload_files}


@router.delete("/delete_files/")
async def delete_files(db: Session = Depends(get_db)):
    """
    Delete all uploaded files from the system and database.
    """
    return delete_all_files(db)


@router.get("/query")
async def rag(query_text: str):
    """
    Perform a retrieval-augmented generation (RAG) query using stored documents.
    """
    documents = SimpleDirectoryReader(DATA_PATH).load_data()
    if not documents:
        raise HTTPException(status_code=404, detail="No documents found")

    rag = query_rag(query_text, documents)
    response = {
        "answer": rag.response,
        "sources": [
            {
                "text": node.text,
                "score": node.score,
                "source": node.metadata.get("source", "Unknown"),
            }
            for node in rag.source_nodes
        ],
    }
    return response
