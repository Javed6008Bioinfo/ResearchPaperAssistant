"""
Shared data contract for the embeddings service.

EmbeddedChunk is the output of Module 5 and the input to Module 6
(Vector Database). It wraps a DocumentChunk (from Module 4) rather than
duplicating its fields, so all provenance information (page number,
source filename, chunk_id) flows through unchanged.
"""

from dataclasses import dataclass

from app.services.text_chunking.schemas import DocumentChunk


@dataclass
class EmbeddedChunk:
    """
    A DocumentChunk paired with its dense vector embedding.

    Attributes:
        chunk: The original DocumentChunk (content + provenance metadata).
        embedding: The dense vector representation of chunk.content,
                   as a plain list of floats (JSON/ChromaDB-friendly —
                   avoids leaking numpy arrays into Module 6's interface).
        embedding_model_name: Name of the model used to generate this
                   vector. Stored per-chunk (not just globally) so that
                   if the app's configured model changes over time,
                   old vectors can be identified and re-embedded rather
                   than silently mixed with incompatible new vectors.
        embedding_dimension: Length of the embedding vector, cached for
                   quick validation/display without recomputation.
    """

    chunk: DocumentChunk
    embedding: list[float]
    embedding_model_name: str
    embedding_dimension: int