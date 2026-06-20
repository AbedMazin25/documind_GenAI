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
    user_count = db.query(User).filter(
        User.org_id == admin.org_id, User.is_active == True
    ).count()
    thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).date()

    query_rows = (
        db.query(
            func.date(AuditLog.created_at).label("day"),
            func.count(AuditLog.id).label("count"),
        )
        .filter(
            AuditLog.org_id == admin.org_id,
            AuditLog.action == "query",
            AuditLog.created_at >= thirty_days_ago,
        )
        .group_by(func.date(AuditLog.created_at))
        .all()
    )
    counts_by_day = {str(row.day): int(row.count) for row in query_rows}

    query_trend = []
    total_queries = 0
    for i in range(29, -1, -1):
        day = (datetime.utcnow() - timedelta(days=i)).date().isoformat()
        c = counts_by_day.get(day, 0)
        total_queries += c
        query_trend.append({"date": day[5:], "count": c})

    return {
        "total_documents": doc_count,
        "total_queries": total_queries,
        "active_users": user_count,
        "query_trend": query_trend,
    }

@router.get("/analytics")
def analytics(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    fourteen_days_ago = (datetime.utcnow() - timedelta(days=14)).date()
    rows = (
        db.query(
            func.date(AuditLog.created_at).label("day"),
            func.count(AuditLog.id).label("count"),
        )
        .filter(
            AuditLog.org_id == admin.org_id,
            AuditLog.action == "query",
            AuditLog.created_at >= fourteen_days_ago,
        )
        .group_by(func.date(AuditLog.created_at))
        .all()
    )
    counts_by_day = {str(r.day): int(r.count) for r in rows}
    queries_by_day = []
    for i in range(13, -1, -1):
        day = (datetime.utcnow() - timedelta(days=i)).date().isoformat()
        queries_by_day.append({"date": day[5:], "count": counts_by_day.get(day, 0)})

    type_rows = (
        db.query(Document.mime_type, func.count(Document.id))
        .filter(Document.org_id == admin.org_id)
        .group_by(Document.mime_type)
        .all()
    )
    label_map = {
        "application/pdf": "PDF",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCX",
        "application/msword": "DOC",
        "text/plain": "TXT",
    }
    docs_by_type = [
        {"type": label_map.get(mime, mime or "Unknown"), "count": int(count)}
        for mime, count in type_rows
    ]

    return {"queries_by_day": queries_by_day, "docs_by_type": docs_by_type}


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
