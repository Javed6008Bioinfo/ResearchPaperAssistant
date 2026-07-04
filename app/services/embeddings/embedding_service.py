"""
Orchestration layer for generating embeddings from DocumentChunks.

This is the main entry point other modules should import from. It
handles batch encoding of document chunks (for indexing, Module 6) and
single-text encoding (for user queries at retrieval time, Module 8),
using the same underlying model so vectors are always comparable.
"""

from app.services.embeddings.embedding_model import get_embedding_model
from app.services.embeddings.schemas import EmbeddedChunk
from app.services.text_chunking.schemas import DocumentChunk
from app.utils.exceptions import EmbeddingGenerationError
from app.utils.logger import logger

# Batch size balances memory usage against speed. 32 is a well-tested
# default for all-MiniLM-L6-v2 on CPU; large batches on CPU show
# diminishing returns and risk memory spikes on constrained deployment
# environments (e.g., free-tier Hugging Face Spaces).
DEFAULT_BATCH_SIZE = 32


def embed_chunks(
    chunks: list[DocumentChunk],
    model_name: str | None = None,
    batch_size: int = DEFAULT_BATCH_SIZE,
    show_progress: bool = False,
) -> list[EmbeddedChunk]:
    """
    Generates embeddings for a list of DocumentChunks.

    Args:
        chunks: DocumentChunk objects produced by Module 4's chunking
                service. Must be non-empty.
        model_name: Optional override for the embedding model.
                Defaults to config/settings.py's configured model.
        batch_size: Number of chunks encoded per forward pass.
        show_progress: Whether to display a progress bar (useful for
                long-running CLI/notebook use; typically False in the
                Streamlit UI, which will show its own spinner instead).

    Returns:
        A list of EmbeddedChunk objects, one per input chunk, in the
        same order as the input.

    Raises:
        EmbeddingGenerationError: If chunks is empty, or embedding
                generation fails for any reason.
    """
    if not chunks:
        raise EmbeddingGenerationError("Cannot embed an empty list of chunks.")

    model = get_embedding_model(model_name)
    resolved_model_name = model_name or model.tokenizer.name_or_path

    texts = [chunk.content for chunk in chunks]

    try:
        vectors = model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=True,  # unit-length vectors -> cosine sim == dot product
            convert_to_numpy=True,
        )
    except Exception as exc:
        raise EmbeddingGenerationError(
            f"Failed to generate embeddings for {len(chunks)} chunk(s): {exc}"
        ) from exc

    embedding_dimension = model.get_sentence_embedding_dimension()

    embedded_chunks = [
        EmbeddedChunk(
            chunk=chunk,
            embedding=vector.tolist(),  # plain list — JSON/ChromaDB-friendly
            embedding_model_name=resolved_model_name,
            embedding_dimension=embedding_dimension,
        )
        for chunk, vector in zip(chunks, vectors)
    ]

    logger.info(
        f"Generated {len(embedded_chunks)} embedding(s) "
        f"(dimension={embedding_dimension}, model='{resolved_model_name}')."
    )
    return embedded_chunks


def embed_query(query_text: str, model_name: str | None = None) -> list[float]:
    """
    Generates a single embedding for a user query string.

    Kept separate from embed_chunks (rather than wrapping the query in
    a list and reusing that function) because query-time embedding has
    different call-site semantics — Module 8's retriever will call this
    directly with raw user input, not a DocumentChunk.

    Args:
        query_text: The raw user question/text to embed.
        model_name: Optional override for the embedding model. Must
                match whatever model was used to embed the stored
                chunks, or similarity scores will be meaningless —
                defaulting both to config/settings.py's single source
                of truth prevents this mismatch by construction.

    Returns:
        A single embedding vector as a list of floats.

    Raises:
        EmbeddingGenerationError: If query_text is empty or embedding fails.
    """
    if not query_text or not query_text.strip():
        raise EmbeddingGenerationError("Cannot embed an empty query string.")

    model = get_embedding_model(model_name)

    try:
        vector = model.encode(
            query_text,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
    except Exception as exc:
        raise EmbeddingGenerationError(f"Failed to embed query text: {exc}") from exc

    return vector.tolist()