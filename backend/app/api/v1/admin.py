from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.document import Document
from app.api.deps import require_admin

router = APIRouter()

@router.get("/stats")
def org_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    doc_count = db.query(Document).filter(Document.org_id == admin.org_id).count()
    user_count = db.query(User).filter(User.org_id == admin.org_id).count()
    return {"documents": doc_count, "users": user_count}

@router.delete("/documents/{doc_id}", status_code=204)
def delete_document(
    doc_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    doc = db.query(Document).filter(
        Document.id == doc_id,
        Document.org_id == admin.org_id,
    ).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    db.delete(doc)
    db.commit()
