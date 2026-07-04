"""
Test suite for the text_chunking service.

Covers: basic splitting behavior, overlap correctness, page-provenance
tracking, deterministic chunk IDs, invalid parameters, empty documents,
and end-to-end integration with Module 3's document_loader output.
"""

from pathlib import Path

import pytest

from app.services.document_loader.schemas import LoadedDocument
from app.services.text_chunking import (
    chunk_loaded_document,
    chunk_plain_text,
)
from app.services.text_chunking.chunker import (
    build_text_splitter,
    split_text,
    validate_chunk_params,
)
from app.utils.exceptions import TextChunkingError


# --- Fixtures ---

@pytest.fixture
def long_text() -> str:
    """~500-word synthetic text simulating a paper section."""
    sentence = "Gene expression was measured using RNA sequencing techniques. "
    return sentence * 50  # ~3200 characters


@pytest.fixture
def multi_page_document(long_text: str) -> LoadedDocument:
    """Simulates a 3-page PDF LoadedDocument."""
    pages = [long_text, long_text, "Short final page about conclusions."]
    return LoadedDocument(
        filename="test_paper.pdf",
        file_type="pdf",
        full_text="\n\n".join(pages),
        pages=pages,
        page_count=3,
    )


@pytest.fixture
def single_page_document(long_text: str) -> LoadedDocument:
    """Simulates a DOCX/TXT LoadedDocument (single logical page)."""
    return LoadedDocument(
        filename="test_notes.docx",
        file_type="docx",
        full_text=long_text,
        pages=[long_text],
        page_count=1,
    )


@pytest.fixture
def empty_document() -> LoadedDocument:
    return LoadedDocument(
        filename="blank.pdf",
        file_type="pdf",
        full_text="",
        pages=["", ""],
        page_count=2,
    )


# --- Parameter validation tests ---

def test_validate_chunk_params_rejects_zero_size() -> None:
    with pytest.raises(TextChunkingError):
        validate_chunk_params(chunk_size=0, chunk_overlap=10)


def test_validate_chunk_params_rejects_negative_overlap() -> None:
    with pytest.raises(TextChunkingError):
        validate_chunk_params(chunk_size=500, chunk_overlap=-5)


def test_validate_chunk_params_rejects_overlap_greater_than_size() -> None:
    with pytest.raises(TextChunkingError):
        validate_chunk_params(chunk_size=200, chunk_overlap=200)


def test_validate_chunk_params_accepts_valid_values() -> None:
    validate_chunk_params(chunk_size=1000, chunk_overlap=150)  # should not raise


# --- Splitter mechanics tests ---

def test_build_text_splitter_returns_configured_instance() -> None:
    splitter = build_text_splitter(chunk_size=500, chunk_overlap=50)
    assert splitter._chunk_size == 500
    assert splitter._chunk_overlap == 50


def test_split_text_respects_chunk_size(long_text: str) -> None:
    chunks = split_text(long_text, chunk_size=500, chunk_overlap=50)
    assert len(chunks) > 1
    # RecursiveCharacterTextSplitter targets chunk_size but may slightly
    # exceed it when preserving whole separators — allow small margin.
    assert all(len(chunk) <= 550 for chunk in chunks)


def test_split_text_empty_input_returns_empty_list() -> None:
    assert split_text("   ", chunk_size=500, chunk_overlap=50) == []
    assert split_text("", chunk_size=500, chunk_overlap=50) == []


def test_split_text_overlap_creates_shared_content(long_text: str) -> None:
    chunks = split_text(long_text, chunk_size=500, chunk_overlap=100)
    # Verify consecutive chunks share some trailing/leading content
    # (exact overlap varies due to separator-aware splitting, so we
    # check for meaningful shared substring rather than exact length).
    first_chunk_tail = chunks[0][-50:]
    assert any(word in chunks[1] for word in first_chunk_tail.split())


# --- Document chunking (orchestration) tests ---

def test_chunk_loaded_document_preserves_page_numbers(multi_page_document: LoadedDocument) -> None:
    chunks = chunk_loaded_document(multi_page_document, chunk_size=500, chunk_overlap=50)

    page_numbers_present = {chunk.page_number for chunk in chunks}
    assert page_numbers_present == {1, 2, 3}

    # Chunks from page 3 (short page) should all be tagged page_number=3
    page_3_chunks = [c for c in chunks if c.page_number == 3]
    assert len(page_3_chunks) >= 1
    assert all("conclusions" in c.content.lower() for c in page_3_chunks)


def test_chunk_loaded_document_global_index_is_sequential(multi_page_document: LoadedDocument) -> None:
    chunks = chunk_loaded_document(multi_page_document, chunk_size=500, chunk_overlap=50)
    indices = [c.chunk_index for c in chunks]
    assert indices == list(range(len(chunks)))  # strictly sequential, no gaps


def test_chunk_loaded_document_single_page(single_page_document: LoadedDocument) -> None:
    chunks = chunk_loaded_document(single_page_document, chunk_size=500, chunk_overlap=50)
    assert all(c.page_number == 1 for c in chunks)
    assert all(c.file_type == "docx" for c in chunks)


def test_chunk_loaded_document_chunk_ids_are_deterministic(single_page_document: LoadedDocument) -> None:
    chunks_run_1 = chunk_loaded_document(single_page_document, chunk_size=500, chunk_overlap=50)
    chunks_run_2 = chunk_loaded_document(single_page_document, chunk_size=500, chunk_overlap=50)

    ids_1 = [c.chunk_id for c in chunks_run_1]
    ids_2 = [c.chunk_id for c in chunks_run_2]
    assert ids_1 == ids_2  # same input + params => same IDs, every time


def test_chunk_loaded_document_empty_document_raises(empty_document: LoadedDocument) -> None:
    with pytest.raises(TextChunkingError):
        chunk_loaded_document(empty_document)


def test_chunk_loaded_document_invalid_params_raise(single_page_document: LoadedDocument) -> None:
    with pytest.raises(TextChunkingError):
        chunk_loaded_document(single_page_document, chunk_size=100, chunk_overlap=100)


# --- Plain text chunking tests ---

def test_chunk_plain_text_success(long_text: str) -> None:
    chunks = chunk_plain_text(long_text, source_label="pasted_abstract", chunk_size=500, chunk_overlap=50)
    assert len(chunks) > 1
    assert all(c.source_filename == "pasted_abstract" for c in chunks)
    assert all(c.page_number == 1 for c in chunks)


def test_chunk_plain_text_empty_raises() -> None:
    with pytest.raises(TextChunkingError):
        chunk_plain_text("", source_label="empty_source")


# --- Integration test with Module 3's real document loader ---

def test_integration_with_document_loader(tmp_path: Path) -> None:
    """
    End-to-end check: Module 3 loads a real file, Module 4 chunks it,
    confirming the two modules' contracts fit together correctly.
    """
    from app.services.document_loader import load_document

    file_path = tmp_path / "integration_sample.txt"
    file_path.write_text(
        "Abstract: This study examines CRISPR-Cas9 mediated gene editing "
        "efficiency across multiple cell lines. " * 30
    )

    document = load_document(file_path)
    chunks = chunk_loaded_document(document, chunk_size=400, chunk_overlap=40)

    assert len(chunks) > 1
    assert all(c.source_filename == "integration_sample.txt" for c in chunks)
    assert all(c.file_type == "txt" for c in chunks)