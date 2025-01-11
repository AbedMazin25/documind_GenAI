import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum

class DocumentStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    indexed = "indexed"
    failed = "failed"

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("orgs.id"), nullable=False, index=True)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    s3_key = Column(String(1000), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    status = Column(Enum(DocumentStatus), default=DocumentStatus.pending)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    indexed_at = Column(DateTime)

    org = relationship("Org", back_populates="documents")
