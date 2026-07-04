"""
Shared data contract for the vector store service.

RetrievedChunk is the output of Module 6's similarity_search() and the
input to Module 8 (RAG Pipeline). It carries everything the LLM prompt
and Module 10's citation display will need, without exposing any raw
ChromaDB response structures to calling code.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RetrievedChunk:
    """
    A single chunk retrieved from the vector store via similarity search,
    ranked by relevance to a query.

    Attributes:
        chunk_id: The deterministic chunk ID assigned in Module 4,
                  preserved through storage and retrieval.
        content: The chunk's text content, ready to be inserted into
                  an LLM prompt (Module 8) or displayed as a citation
                  excerpt (Module 10).
        source_filename: Which paper this chunk came from — essential
                  once multiple papers exist in the same collection.
        page_number: Source page number, for citation display.
        chunk_index: Original position within the source document.
        file_type: Original file format ("pdf", "docx", "txt").
        similarity_score: Cosine similarity to the query, in [-1, 1]
                  (in practice typically [0, 1] for normalized text
                  embeddings). Higher is more relevant. Derived from
                  ChromaDB's distance metric, not returned raw, so
                  callers never need to know "lower distance = better."
        metadata: The raw metadata dict as stored in ChromaDB, kept for
                  forward-compatibility with future metadata fields
                  (e.g., section labels added by Module 11) without
                  requiring a schema change here.
    """

    chunk_id: str
    content: str
    source_filename: str
    page_number: int
    chunk_index: int
    file_type: str
    similarity_score: float
    metadata: dict[str, Any] = field(default_factory=dict)