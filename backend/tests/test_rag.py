import pytest
from unittest.mock import patch, MagicMock
from app.rag.chunkers import chunk_text, split_paragraphs

def test_split_paragraphs_blank_line():
    text = "First paragraph here.\n\nSecond paragraph here.\n\nThird paragraph."
    parts = split_paragraphs(text)
    assert len(parts) == 3
    assert parts[0] == "First paragraph here."

def test_split_paragraphs_single_newline_not_split():
    text = "Line one.\nLine two still same paragraph.\n\nNew paragraph."
    parts = split_paragraphs(text)
    assert len(parts) == 2

def test_chunk_text_basic():
    text = "word " * 600
    chunks = chunk_text(text, chunk_size=100, overlap=10)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c.split()) <= 110

def test_chunk_text_empty():
    chunks = chunk_text("", chunk_size=100, overlap=10)
    assert chunks == []

def test_chunk_text_short_no_split():
    text = "Short text."
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) == 1
    assert chunks[0] == "Short text."
