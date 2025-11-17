from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.db.session import get_db
from app.models.user import User
from app.models.document import Document
from app.models.audit import AuditLog
from app.api.deps import require_admin

router = APIRouter()

@router.get("/stats")
def org_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    doc_count = db.query(Document).filter(Document.org_id == admin.org_id).count()
    user_count = db.query(User).filter(User.org_id == admin.org_id).count()
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    queries_30d = db.query(func.count(AuditLog.id)).filter(
        AuditLog.org_id == admin.org_id,
        AuditLog.action == "query",
        AuditLog.created_at >= thirty_days_ago,
    ).scalar()
    return {"documents": doc_count, "users": user_count, "queries_30d": queries_30d}

@router.get("/audit")
def audit_log(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    q = db.query(AuditLog).filter(AuditLog.org_id == admin.org_id)
    total = q.count()
    logs = q.order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "page": page, "items": logs}

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
