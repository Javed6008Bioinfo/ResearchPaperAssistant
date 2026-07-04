"""
Public API for the embeddings service package.

Module 6 (Vector Database) and Module 8 (RAG Pipeline) should import
from this package root rather than reaching into individual files.
"""

from app.services.embeddings.schemas import EmbeddedChunk
from app.services.embeddings.embedding_service import (
    embed_chunks,
    embed_query,
    DEFAULT_BATCH_SIZE,
)
from app.services.embeddings.embedding_model import get_embedding_model, clear_model_cache

__all__ = [
    "EmbeddedChunk",
    "embed_chunks",
    "embed_query",
    "DEFAULT_BATCH_SIZE",
    "get_embedding_model",
    "clear_model_cache",
]