import io
from pypdf import PdfReader
from docx import Document as DocxDocument
from app.services.storage import StorageService
from app.rag.chunkers import chunk_text

storage = StorageService()

class DocumentProcessor:
    def process(self, s3_key: str, mime_type: str) -> list[str]:
        raw = storage.download(s3_key)
        if mime_type == "application/pdf":
            return self._process_pdf(raw)
        elif mime_type in (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
        ):
            return self._process_docx(raw)
        elif mime_type == "text/plain":
            return self._process_txt(raw)
        raise ValueError(f"Unsupported mime type: {mime_type}")

    def _process_pdf(self, data: bytes) -> list[str]:
        reader = PdfReader(io.BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
        return chunk_text("\n\n".join(pages))

    def _process_docx(self, data: bytes) -> list[str]:
        doc = DocxDocument(io.BytesIO(data))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return chunk_text("\n\n".join(paragraphs))

    def _process_txt(self, data: bytes) -> list[str]:
        return chunk_text(data.decode("utf-8", errors="replace"))
