"""
Singleton loader for the sentence-transformers embedding model.

Loading all-MiniLM-L6-v2 involves reading model weights from disk (or
downloading them on first run) — an expensive operation that must NOT
happen on every Streamlit script rerun or every chunk batch. This module
guarantees the model is loaded exactly once per process and reused
thereafter.
"""

import torch
from sentence_transformers import SentenceTransformer

from config.settings import settings
from app.utils.exceptions import EmbeddingGenerationError
from app.utils.logger import logger

# Module-level cache — persists for the lifetime of the Python process.
# This is safe for Streamlit: the process stays alive across reruns
# within a session, so the model loads once per app launch, not once
# per interaction.
_model_cache: dict[str, SentenceTransformer] = {}


def _resolve_device() -> str:
    """
    Selects the best available device for inference.

    Returns "cuda" if a GPU is available, otherwise "cpu". Bioinformatics
    students and most deployment targets (Hugging Face Spaces free tier,
    Render) typically run CPU-only, so all-MiniLM-L6-v2 was specifically
    chosen for this project because it's small and fast enough for
    practical CPU inference.
    """
    return "cuda" if torch.cuda.is_available() else "cpu"


def get_embedding_model(model_name: str | None = None) -> SentenceTransformer:
    """
    Returns a cached SentenceTransformer instance, loading it on first call.

    Args:
        model_name: Hugging Face model identifier. Defaults to the value
                    configured in config/settings.py so the whole app
                    stays consistent unless explicitly overridden
                    (e.g., in tests).

    Returns:
        A loaded SentenceTransformer ready for encoding.

    Raises:
        EmbeddingGenerationError: If the model fails to load (e.g., no
                    internet connection on first run and no local cache,
                    or an invalid model name).
    """
    resolved_name = model_name or settings.embedding_model_name

    if resolved_name in _model_cache:
        return _model_cache[resolved_name]

    device = _resolve_device()
    logger.info(f"Loading embedding model '{resolved_name}' on device '{device}'...")

    try:
        model = SentenceTransformer(resolved_name, device=device)
    except Exception as exc:
        raise EmbeddingGenerationError(
            f"Failed to load embedding model '{resolved_name}': {exc}"
        ) from exc

    _model_cache[resolved_name] = model
    logger.info(
        f"Embedding model '{resolved_name}' loaded successfully "
        f"(dimension={model.get_sentence_embedding_dimension()})."
    )
    return model


def clear_model_cache() -> None:
    """
    Clears the cached model(s).

    Primarily useful for tests that need to verify fresh-load behavior,
    or if the app ever needs to switch embedding models at runtime
    without restarting the process.
    """
    _model_cache.clear()
    logger.debug("Embedding model cache cleared.")