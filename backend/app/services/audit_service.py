from sqlalchemy.orm import Session
from app.models.audit import AuditLog
from typing import Optional
import uuid

class AuditService:
    def log(
        self,
        db: Session,
        org_id: str,
        user_id: Optional[str],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        entry = AuditLog(
            id=uuid.uuid4(),
            org_id=org_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            extra=metadata or {},
            ip_address=ip_address,
        )
        db.add(entry)
        db.commit()
        return entry
