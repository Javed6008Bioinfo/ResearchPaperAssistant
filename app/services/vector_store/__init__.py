"""
Public API for the vector_store service package.

Module 8 (RAG Pipeline) should import from this package root rather
than reaching into vector_store_service.py or the infrastructure
client directly.
"""

from app.services.vector_store.schemas import RetrievedChunk
from app.services.vector_store.vector_store_service import (
    add_embedded_chunks,
    similarity_search,
    delete_document,
    get_collection_count,
    list_indexed_filenames,
    DEFAULT_TOP_K,
)

__all__ = [
    "RetrievedChunk",
    "add_embedded_chunks",
    "similarity_search",
    "delete_document",
    "get_collection_count",
    "list_indexed_filenames",
    "DEFAULT_TOP_K",
]