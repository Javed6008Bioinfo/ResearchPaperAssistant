"""
LangChain text splitter construction and validation.

This file owns ONLY the mechanics of building a correctly configured
RecursiveCharacterTextSplitter and applying it to raw strings. It has no
knowledge of LoadedDocument, pages, or chunk IDs — that orchestration
lives in chunking_service.py. This separation means if we ever swap
RecursiveCharacterTextSplitter for a different splitting strategy
(e.g., a semantic splitter), only this file changes.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.utils.exceptions import TextChunkingError
from app.utils.logger import logger

# Separator priority for scientific/research text: try to split on
# paragraph breaks first, then lines, then sentences, then words, and
# only as a last resort mid-word. This ordering preserves semantic
# units (sentences, paragraphs) as much as possible.
DEFAULT_SEPARATORS: list[str] = ["\n\n", "\n", ". ", " ", ""]


def validate_chunk_params(chunk_size: int, chunk_overlap: int) -> None:
    """
    Validates chunk_size/chunk_overlap before constructing a splitter.

    Raises:
        TextChunkingError: If parameters are non-positive or overlap
                            is not strictly smaller than chunk_size
                            (which would cause infinite/degenerate
                            splitting behavior).
    """
    if chunk_size <= 0:
        raise TextChunkingError(f"chunk_size must be positive, got {chunk_size}.")

    if chunk_overlap < 0:
        raise TextChunkingError(f"chunk_overlap cannot be negative, got {chunk_overlap}.")

    if chunk_overlap >= chunk_size:
        raise TextChunkingError(
            f"chunk_overlap ({chunk_overlap}) must be smaller than "
            f"chunk_size ({chunk_size})."
        )


def build_text_splitter(chunk_size: int, chunk_overlap: int) -> RecursiveCharacterTextSplitter:
    """
    Factory for a validated RecursiveCharacterTextSplitter.

    Args:
        chunk_size: Target maximum characters per chunk.
        chunk_overlap: Characters shared between consecutive chunks,
                        used to preserve context across chunk boundaries.

    Returns:
        A configured RecursiveCharacterTextSplitter instance.

    Raises:
        TextChunkingError: If parameters are invalid.
    """
    validate_chunk_params(chunk_size, chunk_overlap)

    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=DEFAULT_SEPARATORS,
        length_function=len,
    )


def split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """
    Splits a single string of text into chunks using the configured
    RecursiveCharacterTextSplitter.

    Args:
        text: Raw text to split. Empty/whitespace-only text returns
              an empty list rather than raising, since callers
              iterating over multiple pages shouldn't need special
              casing for blank pages.
        chunk_size: Target maximum characters per chunk.
        chunk_overlap: Characters shared between consecutive chunks.

    Returns:
        List of text chunks in order. Empty list if `text` is blank.

    Raises:
        TextChunkingError: If parameters are invalid or splitting fails.
    """
    if not text or not text.strip():
        return []

    splitter = build_text_splitter(chunk_size, chunk_overlap)

    try:
        chunks = splitter.split_text(text)
    except Exception as exc:
        raise TextChunkingError(f"Failed to split text: {exc}") from exc

    logger.debug(f"Split {len(text)} characters into {len(chunks)} chunk(s).")
    return chunks