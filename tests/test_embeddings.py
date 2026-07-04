"""
Test suite for the embeddings service.

Covers: model loading/caching, embedding dimensionality, batch
correctness, determinism, normalization, empty-input handling, and
end-to-end integration with Module 4's chunking output.

NOTE: These tests download/load the real all-MiniLM-L6-v2 model
(~80MB) on first run. This is intentional — mocking sentence-transformers
would not catch real integration issues (dimension mismatches, API
changes). First run will be slower; subsequent runs use the local
Hugging Face cache.
"""

import math

import pytest

from app.services.embeddings import embed_chunks, embed_query, clear_model_cache
from app.services.embeddings.embedding_model import get_embedding_model
from app.services.text_chunking.schemas import DocumentChunk
from app.utils.exceptions import EmbeddingGenerationError

EXPECTED_DIMENSION = 384  # all-MiniLM-L6-v2's known output dimension


@pytest.fixture
def sample_chunks() -> list[DocumentChunk]:
    return [
        DocumentChunk(
            chunk_id="chunk_1",
            content="CRISPR-Cas9 is a gene editing technology.",
            chunk_index=0,
            page_number=1,
            source_filename="paper1.txt",
            file_type="txt",
            char_count=42,
        ),
        DocumentChunk(
            chunk_id="chunk_2",
            content="RNA sequencing measures gene expression levels.",
            chunk_index=1,
            page_number=1,
            source_filename="paper1.txt",
            file_type="txt",
            char_count=48,
        ),
    ]


# --- Model loading tests ---

def test_get_embedding_model_returns_correct_dimension() -> None:
    model = get_embedding_model()
    assert model.get_sentence_embedding_dimension() == EXPECTED_DIMENSION


def test_get_embedding_model_is_cached_singleton() -> None:
    model_1 = get_embedding_model()
    model_2 = get_embedding_model()
    assert model_1 is model_2  # same object, not just equal


def test_get_embedding_model_invalid_name_raises() -> None:
    clear_model_cache()
    with pytest.raises(EmbeddingGenerationError):
        get_embedding_model("this-model-does-not-exist-12345")


# --- Batch embedding tests ---

def test_embed_chunks_returns_one_embedding_per_chunk(sample_chunks: list[DocumentChunk]) -> None:
    embedded = embed_chunks(sample_chunks)
    assert len(embedded) == len(sample_chunks)


def test_embed_chunks_preserves_order_and_provenance(sample_chunks: list[DocumentChunk]) -> None:
    embedded = embed_chunks(sample_chunks)
    assert embedded[0].chunk.chunk_id == "chunk_1"
    assert embedded[1].chunk.chunk_id == "chunk_2"
    assert embedded[0].chunk.source_filename == "paper1.txt"


def test_embed_chunks_correct_dimension(sample_chunks: list[DocumentChunk]) -> None:
    embedded = embed_chunks(sample_chunks)
    for item in embedded:
        assert item.embedding_dimension == EXPECTED_DIMENSION
        assert len(item.embedding) == EXPECTED_DIMENSION


def test_embed_chunks_vectors_are_normalized(sample_chunks: list[DocumentChunk]) -> None:
    embedded = embed_chunks(sample_chunks)
    for item in embedded:
        magnitude = math.sqrt(sum(x * x for x in item.embedding))
        assert math.isclose(magnitude, 1.0, abs_tol=1e-3)  # unit-length vector


def test_embed_chunks_empty_list_raises() -> None:
    with pytest.raises(EmbeddingGenerationError):
        embed_chunks([])


def test_embed_chunks_records_model_name(sample_chunks: list[DocumentChunk]) -> None:
    embedded = embed_chunks(sample_chunks)
    assert all(item.embedding_model_name for item in embedded)


# --- Determinism test ---

def test_embed_chunks_is_deterministic(sample_chunks: list[DocumentChunk]) -> None:
    """Same input text must always produce the same vector (no randomness)."""
    embedded_run_1 = embed_chunks(sample_chunks)
    embedded_run_2 = embed_chunks(sample_chunks)

    for item_1, item_2 in zip(embedded_run_1, embedded_run_2):
        assert item_1.embedding == pytest.approx(item_2.embedding, abs=1e-6)


# --- Semantic sanity test ---

def test_similar_texts_produce_closer_embeddings(sample_chunks: list[DocumentChunk]) -> None:
    """
    Sanity check that embeddings capture semantic meaning: a query about
    'gene editing' should be closer to the CRISPR chunk than a query
    about an unrelated topic like cooking.
    """
    embedded = embed_chunks(sample_chunks)
    crispr_vector = embedded[0].embedding  # "CRISPR-Cas9 is a gene editing technology."

    query_related = embed_query("What is gene editing?")
    query_unrelated = embed_query("How do I bake a chocolate cake?")

    def cosine_similarity(a: list[float], b: list[float]) -> float:
        return sum(x * y for x, y in zip(a, b))  # vectors are normalized -> dot product = cosine sim

    sim_related = cosine_similarity(crispr_vector, query_related)
    sim_unrelated = cosine_similarity(crispr_vector, query_unrelated)

    assert sim_related > sim_unrelated


# --- Query embedding tests ---

def test_embed_query_returns_correct_dimension() -> None:
    vector = embed_query("What genes are associated with breast cancer?")
    assert len(vector) == EXPECTED_DIMENSION


def test_embed_query_empty_string_raises() -> None:
    with pytest.raises(EmbeddingGenerationError):
        embed_query("   ")


# --- Integration test with Module 4's chunking service ---

def test_integration_with_chunking_service() -> None:
    """
    End-to-end check: Module 4 chunks text, Module 5 embeds those
    chunks, confirming the two modules' contracts fit together.
    """
    from app.services.text_chunking import chunk_plain_text

    chunks = chunk_plain_text(
        "The BRCA1 gene plays a critical role in DNA repair. " * 20,
        source_label="integration_test",
        chunk_size=300,
        chunk_overlap=30,
    )

    embedded = embed_chunks(chunks)
    assert len(embedded) == len(chunks)
    assert all(len(item.embedding) == EXPECTED_DIMENSION for item in embedded)