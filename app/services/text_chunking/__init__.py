"""
Public API for the text_chunking service package.

Other modules (Module 5 embeddings, Module 6 vector store, and any
future UI integration) should import from this package root.
"""

from app.services.text_chunking.schemas import DocumentChunk
from app.services.text_chunking.chunking_service import (
    chunk_loaded_document,
    chunk_plain_text,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
)

__all__ = [
    "DocumentChunk",
    "chunk_loaded_document",
    "chunk_plain_text",
    "DEFAULT_CHUNK_SIZE",
    "DEFAULT_CHUNK_OVERLAP",
]