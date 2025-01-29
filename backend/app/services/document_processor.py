import io
from pypdf import PdfReader
from app.services.storage import StorageService
from app.rag.chunkers import chunk_text

storage = StorageService()

class DocumentProcessor:
    def process(self, s3_key: str, mime_type: str) -> list[str]:
        raw = storage.download(s3_key)
        if mime_type == "application/pdf":
            return self._process_pdf(raw)
        raise ValueError(f"Unsupported mime type: {mime_type}")

    def _process_pdf(self, data: bytes) -> list[str]:
        reader = PdfReader(io.BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
        full_text = "\n\n".join(pages)
        return chunk_text(full_text)
