from app.config import settings

def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> list[str]:
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap
    paragraphs = split_paragraphs(text)
    chunks, current, current_len = [], [], 0
    for para in paragraphs:
        words = para.split()
        if current_len + len(words) > chunk_size and current:
            chunks.append(" ".join(current))
            current = current[-overlap:] if overlap else []
            current_len = len(current)
        current.extend(words)
        current_len += len(words)
    if current:
        chunks.append(" ".join(current))
    return [c for c in chunks if c.strip()]

def split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in text.split("\n\n") if p.strip()]
