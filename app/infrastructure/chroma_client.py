"""
ChromaDB infrastructure client — the ONLY file in the project that
imports the `chromadb` package directly.

Owns connection lifecycle (a persistent client, cached for the process
lifetime) and raw collection access. Contains zero business logic:
no knowledge of DocumentChunk, EmbeddedChunk, or similarity scoring —
that belongs in app/services/vector_store/vector_store_service.py.

This separation means swapping ChromaDB for a different vector database
in the future touches only this file.
"""

from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection

from config.settings import settings
from app.utils.exceptions import VectorStoreError
from app.utils.logger import logger

# Module-level cache — mirrors the singleton pattern used for the
# embedding model in Module 5. Opening a PersistentClient repeatedly
# (e.g., on every Streamlit rerun) would be wasteful and can cause
# file-lock contention on the underlying SQLite store.
_client_cache: dict[str, chromadb.ClientAPI] = {}


def get_chroma_client(persist_directory: str | None = None) -> chromadb.ClientAPI:
    """
    Returns a cached persistent ChromaDB client, creating one on first call.

    Args:
        persist_directory: Optional override for the storage path.
                Defaults to config/settings.py's configured directory.
                Overriding is primarily useful for test isolation.

    Returns:
        A ChromaDB PersistentClient instance.

    Raises:
        VectorStoreError: If the client fails to initialize (e.g.,
                permissions issue on the persist directory).
    """
    resolved_path = persist_directory or settings.chroma_persist_directory

    if resolved_path in _client_cache:
        return _client_cache[resolved_path]

    try:
        Path(resolved_path).mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=resolved_path)
    except Exception as exc:
        raise VectorStoreError(
            f"Failed to initialize ChromaDB client at '{resolved_path}': {exc}"
        ) from exc

    _client_cache[resolved_path] = client
    logger.info(f"ChromaDB persistent client initialized at '{resolved_path}'.")
    return client


def get_or_create_collection(
    collection_name: str | None = None,
    persist_directory: str | None = None,
) -> Collection:
    """
    Returns the app's ChromaDB collection, creating it if it doesn't exist.

    The collection is explicitly configured for cosine similarity space,
    matching Module 5's normalized embeddings (normalize_embeddings=True).
    Mismatching this setting with how embeddings were generated would
    silently produce meaningless similarity scores.

    Args:
        collection_name: Optional override. Defaults to
                config/settings.py's configured collection name.
        persist_directory: Optional override, forwarded to get_chroma_client
                (primarily for test isolation).

    Returns:
        A ChromaDB Collection ready for upsert/query/delete.

    Raises:
        VectorStoreError: If collection creation/retrieval fails.
    """
    client = get_chroma_client(persist_directory)
    resolved_name = collection_name or settings.chroma_collection_name

    try:
        collection = client.get_or_create_collection(
            name=resolved_name,
            metadata={"hnsw:space": "cosine"},
        )
    except Exception as exc:
        raise VectorStoreError(
            f"Failed to get or create collection '{resolved_name}': {exc}"
        ) from exc

    return collection


def delete_collection(collection_name: str | None = None, persist_directory: str | None = None) -> None:
    """
    Permanently deletes a collection and all its vectors.

    Not exposed in the main app UI in this module — primarily a test
    utility and an administrative operation for future use (e.g., a
    "reset library" feature).

    Raises:
        VectorStoreError: If the collection doesn't exist or deletion fails.
    """
    client = get_chroma_client(persist_directory)
    resolved_name = collection_name or settings.chroma_collection_name

    try:
        client.delete_collection(name=resolved_name)
    except Exception as exc:
        raise VectorStoreError(f"Failed to delete collection '{resolved_name}': {exc}") from exc

    logger.info(f"Deleted ChromaDB collection '{resolved_name}'.")


def clear_client_cache() -> None:
    """
    Clears the cached client(s).

    Used by tests to force a fresh client bound to a temporary directory,
    ensuring test isolation from the app's real persisted vector store.
    """
    _client_cache.clear()
    logger.debug("ChromaDB client cache cleared.")