from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.db.session import get_db
from app.models.document import Document, DocumentStatus
from app.models.user import User
from app.api.deps import get_current_user
from app.services.storage import StorageService
import uuid

router = APIRouter()
storage = StorageService()

class DocumentResponse(BaseModel):
    id: uuid.UUID
    filename: str
    status: DocumentStatus
    chunk_count: int

    class Config:
        from_attributes = True

@router.post("/", response_model=DocumentResponse, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s3_key = f"{current_user.org_id}/{uuid.uuid4()}/{file.filename}"
    await storage.upload(file, s3_key)
    doc = Document(
        org_id=current_user.org_id,
        uploaded_by=current_user.id,
        filename=file.filename,
        s3_key=s3_key,
        mime_type=file.content_type,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    background_tasks.add_task(storage.trigger_processing, str(doc.id))
    return doc

@router.get("/", response_model=list[DocumentResponse])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Bug: missing org_id filter — returns documents from all orgs
    return db.query(Document).all()

@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(
    doc_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = db.query(Document).filter(
        Document.id == doc_id,
        Document.org_id == current_user.org_id,
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
