"""
Orchestration layer for chunking a LoadedDocument into DocumentChunks.

This is the main entry point other modules should import from. It walks
a LoadedDocument's pages, applies the configured text splitter to each
page independently (preserving page provenance for citations), and
assembles fully-populated DocumentChunk objects with deterministic IDs.
"""

import hashlib

from app.services.document_loader.schemas import LoadedDocument
from app.services.text_chunking.chunker import split_text, validate_chunk_params
from app.services.text_chunking.schemas import DocumentChunk
from app.utils.exceptions import TextChunkingError
from app.utils.logger import logger

# Defaults mirror config/settings.py so this service works standalone,
# but callers (e.g., a future UI integration) can always override them
# with user-configured values from Settings page.
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 150


def _generate_chunk_id(filename: str, page_number: int, chunk_index: int, content: str) -> str:
    """
    Generates a deterministic, unique chunk ID.

    Deterministic (hash-based) rather than random UUID so that
    re-processing the same document with the same chunking parameters
    yields identical chunk IDs. This is essential for Module 6
    (ChromaDB), where re-uploading the same paper should update/replace
    existing vectors instead of creating duplicates.

    The content hash (not just filename+index) is included so that if
    the source text itself changes, the ID changes too — avoiding stale
    vectors silently persisting after a document is corrected.
    """
    content_fingerprint = hashlib.md5(content.encode("utf-8")).hexdigest()[:8]
    raw_id = f"{filename}_p{page_number}_c{chunk_index}_{content_fingerprint}"
    return hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:24]


def chunk_loaded_document(
    document: LoadedDocument,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[DocumentChunk]:
    """
    Splits a LoadedDocument into a list of DocumentChunk objects.

    Chunking is performed PER PAGE (not on the concatenated full_text)
    so that each resulting chunk retains an accurate page_number for
    citation purposes in Module 10. For DOCX/TXT documents, which have
    only a single logical "page," this simply chunks that one block.

    Args:
        document: A LoadedDocument produced by Module 3's document_loader.
        chunk_size: Target maximum characters per chunk.
        chunk_overlap: Characters shared between consecutive chunks.

    Returns:
        A list of DocumentChunk objects, ordered by (page_number, chunk_index).

    Raises:
        TextChunkingError: If parameters are invalid or the document
                            contains no extractable text to chunk.
    """
    validate_chunk_params(chunk_size, chunk_overlap)

    if document.is_empty():
        raise TextChunkingError(
            f"Cannot chunk '{document.filename}': no extractable text found. "
            "This document may be a scanned/image-based file with no text layer."
        )

    chunks: list[DocumentChunk] = []
    global_chunk_index = 0

    for page_number, page_text in enumerate(document.pages, start=1):
        if not page_text or not page_text.strip():
            # Skip blank pages (common in PDFs with figures/whitespace pages)
            # without breaking page-number continuity for later pages.
            continue

        page_text_chunks = split_text(page_text, chunk_size, chunk_overlap)

        for chunk_text in page_text_chunks:
            chunk_id = _generate_chunk_id(
                filename=document.filename,
                page_number=page_number,
                chunk_index=global_chunk_index,
                content=chunk_text,
            )

            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    content=chunk_text,
                    chunk_index=global_chunk_index,
                    page_number=page_number,
                    source_filename=document.filename,
                    file_type=document.file_type,
                    char_count=len(chunk_text),
                )
            )
            global_chunk_index += 1

    if not chunks:
        raise TextChunkingError(
            f"Chunking '{document.filename}' produced zero chunks despite "
            "non-empty document text. Check chunk_size/chunk_overlap parameters."
        )

    logger.info(
        f"Chunked '{document.filename}' into {len(chunks)} chunk(s) "
        f"(chunk_size={chunk_size}, chunk_overlap={chunk_overlap})."
    )
    return chunks


def chunk_plain_text(
    text: str,
    source_label: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[DocumentChunk]:
    """
    Chunks raw text not tied to a LoadedDocument (e.g., pasted text,
    or text assembled from multiple sources in a future module like
    Module 13's paper comparison).

    Args:
        text: Raw text to chunk.
        source_label: A label identifying where this text came from,
                       stored as `source_filename` on each chunk.
        chunk_size: Target maximum characters per chunk.
        chunk_overlap: Characters shared between consecutive chunks.

    Returns:
        A list of DocumentChunk objects with page_number fixed at 1
        (no pagination concept for arbitrary text).

    Raises:
        TextChunkingError: If parameters are invalid or text is empty.
    """
    if not text or not text.strip():
        raise TextChunkingError(f"Cannot chunk empty text from source '{source_label}'.")

    text_chunks = split_text(text, chunk_size, chunk_overlap)

    return [
        DocumentChunk(
            chunk_id=_generate_chunk_id(source_label, 1, i, chunk_text),
            content=chunk_text,
            chunk_index=i,
            page_number=1,
            source_filename=source_label,
            file_type="text",
            char_count=len(chunk_text),
        )
        for i, chunk_text in enumerate(text_chunks)
    ]