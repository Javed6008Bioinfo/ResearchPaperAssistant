"""
Test suite for the vector_store service.

Uses a temporary, isolated ChromaDB persistent directory per test (via
monkeypatching config.settings + clearing the infrastructure client
cache) so tests never touch or pollute the app's real data/vector_store/
directory, and tests don't interfere with each other.

Most tests use small synthetic vectors (not real sentence-transformers
output) since ChromaDB's storage/retrieval logic doesn't depend on
embeddings being semantically meaningful — only the final integration
test exercises the real Module 4 -> 5 -> 6 pipeline end-to-end.
"""

import uuid

import pytest

from app.infrastructure.chroma_client import clear_client_cache
from app.services.embeddings.schemas import EmbeddedChunk
from app.services.text_chunking.schemas import DocumentChunk
from app.services.vector_store import (
    add_embedded_chunks,
    similarity_search,
    delete_document,
    get_collection_count,
    list_indexed_filenames,
)
from app.utils.exceptions import VectorStoreError


@pytest.fixture(autouse=True)
def isolated_chroma_store(tmp_path, monkeypatch):
    """
    Redirects ChromaDB storage to a temporary directory and uses a
    uniquely named collection for every test, guaranteeing full
    isolation from both the real app data and other tests.
    """
    from config.settings import settings

    unique_collection = f"test_collection_{uuid.uuid4().hex[:8]}"
    monkeypatch.setattr(settings, "chroma_persist_directory", str(tmp_path))
    monkeypatch.setattr(settings, "chroma_collection_name", unique_collection)

    clear_client_cache()
    yield
    clear_client_cache()


def _make_embedded_chunk(
    chunk_id: str,
    content: str,
    embedding: list[float],
    filename: str = "paper.pdf",
    page_number: int = 1,
    chunk_index: int = 0,
) -> EmbeddedChunk:
    """Helper to build an EmbeddedChunk without going through Modules 4/5."""
    chunk = DocumentChunk(
        chunk_id=chunk_id,
        content=content,
        chunk_index=chunk_index,
        page_number=page_number,
        source_filename=filename,
        file_type="pdf",
        char_count=len(content),
    )
    return EmbeddedChunk(
        chunk=chunk,
        embedding=embedding,
        embedding_model_name="test-model",
        embedding_dimension=len(embedding),
    )


# --- Storage tests ---

def test_add_embedded_chunks_stores_correct_count() -> None:
    chunks = [
        _make_embedded_chunk("id1", "Gene expression analysis.", [1.0, 0.0, 0.0]),
        _make_embedded_chunk("id2", "Protein folding structure.", [0.0, 1.0, 0.0]),
    ]
    stored_count = add_embedded_chunks(chunks)
    assert stored_count == 2
    assert get_collection_count() == 2


def test_add_embedded_chunks_empty_list_raises() -> None:
    with pytest.raises(VectorStoreError):
        add_embedded_chunks([])


def test_add_embedded_chunks_upsert_avoids_duplicates() -> None:
    """
    Re-adding a chunk with the SAME chunk_id should update it in place,
    not create a duplicate — this is the entire point of Module 4's
    deterministic chunk IDs.
    """
    original = _make_embedded_chunk("stable_id", "Original text.", [1.0, 0.0, 0.0])
    add_embedded_chunks([original])
    assert get_collection_count() == 1

    updated = _make_embedded_chunk("stable_id", "Updated text.", [1.0, 0.0, 0.0])
    add_embedded_chunks([updated])
    assert get_collection_count() == 1  # still 1, not 2

    results = similarity_search([1.0, 0.0, 0.0], top_k=1)
    assert results[0].content == "Updated text."


# --- Retrieval tests ---

def test_similarity_search_returns_most_similar_first() -> None:
    chunks = [
        _make_embedded_chunk("id1", "About cats.", [1.0, 0.0, 0.0]),
        _make_embedded_chunk("id2", "About dogs.", [0.0, 1.0, 0.0]),
        _make_embedded_chunk("id3", "About kittens.", [0.9, 0.1, 0.0]),
    ]
    add_embedded_chunks(chunks)

    # Query vector closest to "cats" and "kittens"
    results = similarity_search([1.0, 0.0, 0.0], top_k=3)

    assert len(results) == 3
    assert results[0].content == "About cats."  # exact match should rank first
    assert results[0].similarity_score >= results[1].similarity_score >= results[2].similarity_score


def test_similarity_search_respects_top_k() -> None:
    chunks = [
        _make_embedded_chunk(f"id{i}", f"Chunk number {i}.", [float(i), 0.0, 0.0])
        for i in range(5)
    ]
    add_embedded_chunks(chunks)

    results = similarity_search([1.0, 0.0, 0.0], top_k=2)
    assert len(results) == 2


def test_similarity_search_on_empty_collection_returns_empty_list() -> None:
    results = similarity_search([1.0, 0.0, 0.0], top_k=4)
    assert results == []


def test_similarity_search_filters_by_source_filename() -> None:
    chunks = [
        _make_embedded_chunk("id1", "Paper A content.", [1.0, 0.0, 0.0], filename="paperA.pdf"),
        _make_embedded_chunk("id2", "Paper B content.", [1.0, 0.0, 0.0], filename="paperB.pdf"),
    ]
    add_embedded_chunks(chunks)

    results = similarity_search([1.0, 0.0, 0.0], top_k=5, source_filename="paperA.pdf")
    assert len(results) == 1
    assert results[0].source_filename == "paperA.pdf"


def test_similarity_search_invalid_params_raise() -> None:
    with pytest.raises(VectorStoreError):
        similarity_search([], top_k=4)

    with pytest.raises(VectorStoreError):
        similarity_search([1.0, 0.0, 0.0], top_k=0)


def test_similarity_search_preserves_metadata() -> None:
    chunks = [_make_embedded_chunk("id1", "Sample text.", [1.0, 0.0, 0.0], page_number=7, chunk_index=3)]
    add_embedded_chunks(chunks)

    results = similarity_search([1.0, 0.0, 0.0], top_k=1)
    assert results[0].page_number == 7
    assert results[0].chunk_index == 3
    assert results[0].chunk_id == "id1"


# --- Deletion tests ---

def test_delete_document_removes_matching_chunks() -> None:
    chunks = [
        _make_embedded_chunk("id1", "Keep me.", [1.0, 0.0, 0.0], filename="keep.pdf"),
        _make_embedded_chunk("id2", "Delete me.", [0.0, 1.0, 0.0], filename="delete.pdf"),
    ]
    add_embedded_chunks(chunks)
    assert get_collection_count() == 2

    deleted_count = delete_document("delete.pdf")
    assert deleted_count == 1
    assert get_collection_count() == 1

    remaining = similarity_search([1.0, 0.0, 0.0], top_k=5)
    assert all(r.source_filename == "keep.pdf" for r in remaining)


def test_delete_document_nonexistent_filename_returns_zero() -> None:
    deleted_count = delete_document("does_not_exist.pdf")
    assert deleted_count == 0


# --- Library listing tests ---

def test_list_indexed_filenames_returns_unique_sorted_names() -> None:
    chunks = [
        _make_embedded_chunk("id1", "A.", [1.0, 0.0, 0.0], filename="zebra.pdf"),
        _make_embedded_chunk("id2", "B.", [0.0, 1.0, 0.0], filename="apple.pdf"),
        _make_embedded_chunk("id3", "C.", [0.0, 0.0, 1.0], filename="apple.pdf"),  # duplicate filename
    ]
    add_embedded_chunks(chunks)

    filenames = list_indexed_filenames()
    assert filenames == ["apple.pdf", "zebra.pdf"]  # deduplicated and sorted


def test_list_indexed_filenames_empty_collection() -> None:
    assert list_indexed_filenames() == []


# --- Full integration test: Modules 4 -> 5 -> 6 ---

def test_integration_full_pipeline() -> None:
    """
    End-to-end check using REAL chunking and embedding (Modules 4 and 5)
    feeding into REAL vector storage and retrieval (Module 6), confirming
    all three modules' contracts fit together correctly.
    """
    from app.services.text_chunking import chunk_plain_text
    from app.services.embeddings import embed_chunks, embed_query

    chunks = chunk_plain_text(
        "CRISPR-Cas9 is a revolutionary gene editing tool used in molecular "
        "biology. It allows precise modification of DNA sequences. " * 15,
        source_label="crispr_paper.txt",
        chunk_size=300,
        chunk_overlap=30,
    )
    embedded = embed_chunks(chunks)
    add_embedded_chunks(embedded)

    assert get_collection_count() == len(chunks)

    query_vector = embed_query("How does CRISPR gene editing work?")
    results = similarity_search(query_vector, top_k=3)

    assert len(results) > 0
    assert all(r.source_filename == "crispr_paper.txt" for r in results)
    assert all(0.0 <= r.similarity_score <= 1.0 + 1e-6 for r in results)