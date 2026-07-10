"""
GOVs-AI Document Upload Routes
POST /api/upload-pdf — upload and ingest PDF for RAG
"""

import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import User, Document
from api.auth import get_current_user
from config import settings

router = APIRouter(prefix="/api", tags=["Documents"])


def _process_pdf(doc_id: int, filepath: str):
    """Background task to ingest uploaded PDF into FAISS."""
    from rag.ingestion import ingest_pdf
    from database.connection import SessionLocal

    db = SessionLocal()
    try:
        chunks = ingest_pdf(filepath)
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.processed = True
            doc.chunks_count = chunks
            db.commit()
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"PDF ingestion failed for {filepath}: {e}")
    finally:
        db.close()


@router.post("/upload-pdf")
def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a PDF file for RAG ingestion."""
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Validate file size
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit",
        )

    # Save file
    filepath = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Create document record
    doc = Document(
        filename=file.filename,
        upload_path=filepath,
        uploaded_by=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Trigger background ingestion
    background_tasks.add_task(_process_pdf, doc.id, filepath)

    return {
        "message": "PDF uploaded successfully. Processing will begin shortly.",
        "document_id": doc.id,
        "filename": file.filename,
    }


@router.get("/documents")
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all uploaded documents."""
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "processed": d.processed,
            "chunks_count": d.chunks_count,
            "created_at": d.created_at.isoformat(),
        }
        for d in docs
    ]
