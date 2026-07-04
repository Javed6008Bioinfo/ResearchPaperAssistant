"""
Orchestration layer for storing and retrieving embedded document chunks
via ChromaDB.

This is the main entry point other modules should import from. It
translates between the app's typed domain objects (EmbeddedChunk,
RetrievedChunk) and ChromaDB's raw dict-based API, so no other module
in the codebase needs to know ChromaDB's response shapes.
"""

from typing import Any

from app.infrastructure.chroma_client import get_or_create_collection
from app.services.embeddings.schemas import EmbeddedChunk
from app.services.vector_store.schemas import RetrievedChunk
from app.utils.exceptions import VectorStoreError
from app.utils.logger import logger

DEFAULT_TOP_K = 4


def add_embedded_chunks(
    embedded_chunks: list[EmbeddedChunk],
    collection_name: str | None = None,
) -> int:
    """
    Stores (or updates) a list of EmbeddedChunks in the vector store.

    Uses ChromaDB's upsert operation keyed on each chunk's deterministic
    chunk_id (assigned in Module 4). This means re-uploading the same
    paper with the same chunking parameters UPDATES existing vectors
    rather than creating duplicates — critical for a usable "re-process
    this paper" flow without manual cleanup.

    Args:
        embedded_chunks: Output of Module 5's embed_chunks(). Must be
                non-empty.
        collection_name: Optional override for the target collection.

    Returns:
        The number of chunks stored.

    Raises:
        VectorStoreError: If embedded_chunks is empty or storage fails.
    """
    if not embedded_chunks:
        raise VectorStoreError("Cannot add an empty list of embedded chunks.")

    collection = get_or_create_collection(collection_name)

    ids: list[str] = []
    embeddings: list[list[float]] = []
    documents: list[str] = []
    metadatas: list[dict[str, Any]] = []

    for item in embedded_chunks:
        chunk = item.chunk
        ids.append(chunk.chunk_id)
        embeddings.append(item.embedding)
        documents.append(chunk.content)
        # ChromaDB metadata values must be str/int/float/bool — no None,
        # no nested structures. We deliberately whitelist fields here
        # rather than dumping chunk.metadata directly, to guarantee
        # this constraint is always satisfied regardless of what future
        # modules add to DocumentChunk.metadata.
        metadatas.append({
            "source_filename": chunk.source_filename,
            "page_number": chunk.page_number,
            "chunk_index": chunk.chunk_index,
            "file_type": chunk.file_type,
            "char_count": chunk.char_count,
            "embedding_model_name": item.embedding_model_name,
        })

    try:
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
    except Exception as exc:
        raise VectorStoreError(f"Failed to store {len(ids)} chunk(s) in ChromaDB: {exc}") from exc

    logger.info(f"Stored/updated {len(ids)} chunk(s) in collection '{collection.name}'.")
    return len(ids)


def similarity_search(
    query_embedding: list[float],
    top_k: int = DEFAULT_TOP_K,
    collection_name: str | None = None,
    source_filename: str | None = None,
) -> list[RetrievedChunk]:
    """
    Retrieves the top-k most similar chunks to a query embedding.

    Args:
        query_embedding: A query vector, produced by Module 5's
                embed_query() using the SAME model used to embed the
                stored chunks (mismatched models produce meaningless scores).
        top_k: Maximum number of chunks to retrieve.
        collection_name: Optional override for which collection to search.
        source_filename: Optional filter to restrict search to a single
                paper — used when the user has selected a specific
                "active paper" to chat with, rather than the whole library.

    Returns:
        A list of RetrievedChunk objects ordered by descending relevance
        (most similar first). Returns an empty list if the collection
        has no stored chunks yet, rather than raising — an empty
        library is a normal, expected state.

    Raises:
        VectorStoreError: If query_embedding is empty, top_k is invalid,
                or the underlying ChromaDB query fails.
    """
    if not query_embedding:
        raise VectorStoreError("query_embedding cannot be empty.")

    if top_k <= 0:
        raise VectorStoreError(f"top_k must be positive, got {top_k}.")

    collection = get_or_create_collection(collection_name)
    stored_count = collection.count()

    if stored_count == 0:
        logger.warning(
            f"similarity_search called on empty collection '{collection.name}'. "
            "Returning no results."
        )
        return []

    where_clause = {"source_filename": source_filename} if source_filename else None

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, stored_count),
            where=where_clause,
        )
    except Exception as exc:
        raise VectorStoreError(f"Similarity search failed: {exc}") from exc

    return _parse_query_results(results)


def _parse_query_results(results: dict[str, Any]) -> list[RetrievedChunk]:
    """
    Converts ChromaDB's raw query response into typed RetrievedChunk objects.

    ChromaDB returns each field as a list-of-lists (outer list = one
    per query embedding submitted; we always submit exactly one query
    at a time), so we always index into position [0].
    """
    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    retrieved_chunks: list[RetrievedChunk] = []
    for chunk_id, content, metadata, distance in zip(ids, documents, metadatas, distances):
        metadata = metadata or {}
        # ChromaDB's cosine space returns distance = 1 - cosine_similarity,
        # so we invert it here — callers of this service should only ever
        # reason in terms of "similarity" (higher = better), never raw
        # distance, to avoid sign-confusion bugs downstream in Module 8.
        similarity_score = 1.0 - distance

        retrieved_chunks.append(
            RetrievedChunk(
                chunk_id=chunk_id,
                content=content,
                source_filename=metadata.get("source_filename", "unknown"),
                page_number=metadata.get("page_number", 1),
                chunk_index=metadata.get("chunk_index", 0),
                file_type=metadata.get("file_type", "unknown"),
                similarity_score=similarity_score,
                metadata=metadata,
            )
        )

    return retrieved_chunks


def delete_document(source_filename: str, collection_name: str | None = None) -> int:
    """
    Deletes all chunks belonging to a specific source document.

    Needed for a "remove paper from library" feature, and for cleanly
    re-processing a document from scratch (delete old chunks, then
    re-add newly chunked/embedded ones) rather than relying solely on
    upsert (which only helps when chunk_ids are unchanged).

    Args:
        source_filename: The filename whose chunks should be removed.
        collection_name: Optional override for the target collection.

    Returns:
        The number of chunks deleted (0 if none were found).

    Raises:
        VectorStoreError: If the deletion operation fails.
    """
    collection = get_or_create_collection(collection_name)

    try:
        matching = collection.get(where={"source_filename": source_filename})
        matching_ids = matching.get("ids", [])

        if not matching_ids:
            logger.info(f"No chunks found for '{source_filename}' — nothing to delete.")
            return 0

        collection.delete(ids=matching_ids)
    except Exception as exc:
        raise VectorStoreError(f"Failed to delete chunks for '{source_filename}': {exc}") from exc

    logger.info(f"Deleted {len(matching_ids)} chunk(s) for '{source_filename}'.")
    return len(matching_ids)


def get_collection_count(collection_name: str | None = None) -> int:
    """
    Returns the total number of chunks currently stored in the collection.

    Useful for library statistics (e.g., a future "N chunks indexed"
    display) and for tests verifying storage/deletion behavior.
    """
    collection = get_or_create_collection(collection_name)
    return collection.count()


def list_indexed_filenames(collection_name: str | None = None) -> list[str]:
    """
    Returns the distinct source filenames currently indexed in the store.

    Reserved primarily for Module 13 (Multiple Paper Comparison), which
    will need to know which papers are available to compare, without
    relying on Streamlit session state (e.g., after an app restart where
    the vector store persisted but session state did not).

    Returns:
        A sorted list of unique filenames. Empty list if the collection
        has no stored chunks.
    """
    collection = get_or_create_collection(collection_name)

    if collection.count() == 0:
        return []

    all_items = collection.get(include=["metadatas"])
    filenames = {
        metadata.get("source_filename")
        for metadata in all_items.get("metadatas", [])
        if metadata and metadata.get("source_filename")
    }
    return sorted(filenames)