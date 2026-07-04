"""
Shared data contract for the text chunking service.

DocumentChunk is the output of Module 4 and the input to Module 5
(Embeddings) and Module 6 (Vector Database). Keeping this schema stable
and well-documented means those modules can be built without ever
importing from chunker.py or chunking_service.py's internals.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DocumentChunk:
    """
    A single chunk of text extracted from a source document, ready for
    embedding and storage.

    Attributes:
        chunk_id: Deterministic, unique identifier for this chunk.
                  Stable across re-runs of the same document/config, so
                  Module 6 can upsert without creating duplicate vectors.
        content: The actual chunk text to be embedded.
        chunk_index: Position of this chunk within the overall document
                     (0-based, global across all pages) — used for
                     ordering and debugging.
        page_number: Source page number (1-based) this chunk was
                     extracted from. For formats without real pagination
                     (DOCX, TXT), this is always 1.
        source_filename: Original filename this chunk came from — needed
                     for citations (Module 10) once multiple papers exist
                     in the vector store.
        file_type: Original file format ("pdf", "docx", "txt").
        char_count: Length of `content` in characters, cached for
                     quick display/debugging without recomputation.
        metadata: Free-form dict for additional context. Reserved for
                     future modules (e.g., section headers detected by
                     Module 11's summarizer, or paper_id once a proper
                     document registry exists).
    """

    chunk_id: str
    content: str
    chunk_index: int
    page_number: int
    source_filename: str
    file_type: str
    char_count: int
    metadata: dict[str, Any] = field(default_factory=dict)