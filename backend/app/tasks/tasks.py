from app.tasks.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.document import Document, DocumentStatus
from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import embed_texts
from app.rag.vectorstore import VectorStore
from app.services.audit_service import AuditService
from datetime import datetime
import uuid

processor = DocumentProcessor()
vector_store = VectorStore()
audit = AuditService()

@celery_app.task(bind=True, max_retries=3)
def process_document(self, doc_id: str):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return
        doc.status = DocumentStatus.processing
        db.commit()

        chunks = processor.process(doc.s3_key, doc.mime_type or "application/pdf")
        embeddings = embed_texts(chunks)

        collection = vector_store.get_or_create_collection(str(doc.org_id))
        ids = [str(uuid.uuid4()) for _ in chunks]
        collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=[{"doc_id": doc_id, "org_id": str(doc.org_id), "chunk": i} for i in range(len(chunks))],
        )

        doc.chunk_count = len(chunks)
        doc.status = DocumentStatus.indexed
        doc.indexed_at = datetime.utcnow()
        db.commit()
        audit.log(db, str(doc.org_id), None, "document.indexed", "document", doc_id)
    except Exception as exc:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.status = DocumentStatus.failed
            db.commit()
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()

@celery_app.task
def sync_sharepoint(org_id: str, site_url: str, library: str):
    from app.integrations.sharepoint import SharePointConnector
    db = SessionLocal()
    connector = SharePointConnector()
    try:
        files = connector.list_files(site_url, library)
        for file_info in files:
            process_document.delay(file_info["doc_id"])
    finally:
        db.close()
