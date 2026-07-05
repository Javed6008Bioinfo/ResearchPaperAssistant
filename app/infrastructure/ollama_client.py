"""
Ollama infrastructure client — the ONLY file in the project that imports
`langchain_ollama` or talks to Ollama's HTTP API directly.

Owns chat model instantiation (a thread-safe, cached ChatOllama per
model+temperature combination) and optional, explicit health-check
calls. Contains zero prompt/business logic — that belongs in
app/services/llm/llm_service.py.

Thread-safety note: Streamlit serves multiple user sessions from the
same process on separate threads. A prior review of this project's
ChromaDB client cache (Module 6) identified an unsynchronized
check-then-set race under concurrent first-access. The same risk exists
here, so the cache below is guarded with a lock from the start.
"""

import threading

import requests
from langchain_ollama import ChatOllama

from config.settings import settings
from app.utils.exceptions import LLMGenerationError
from app.utils.logger import logger

# Cache key is (model_name, temperature) since ChatOllama instances are
# configured per-temperature — different temperature requests need
# different cached instances, not just different model names.
_chat_model_cache: dict[tuple[str, float], ChatOllama] = {}
_cache_lock = threading.Lock()


def get_chat_model(model_name: str, temperature: float) -> ChatOllama:
    """
    Returns a cached ChatOllama instance for the given model+temperature,
    creating one on first request. Thread-safe under concurrent access.

    Args:
        model_name: Ollama model tag (e.g., "llama3", "gemma3"). Must
                already be pulled locally via `ollama pull <model_name>`.
        temperature: Sampling temperature for generation.

    Returns:
        A configured ChatOllama instance.

    Raises:
        LLMGenerationError: If the ChatOllama client fails to initialize.
                Note: this does NOT guarantee the model is reachable or
                pulled — ChatOllama construction is lazy. Failures from
                a missing/unpulled model surface later, at invoke() time.
    """
    cache_key = (model_name, temperature)

    if cache_key in _chat_model_cache:
        return _chat_model_cache[cache_key]

    with _cache_lock:
        # Re-check inside the lock: another thread may have populated
        # the cache while we were waiting to acquire it.
        if cache_key in _chat_model_cache:
            return _chat_model_cache[cache_key]

        try:
            chat_model = ChatOllama(
                model=model_name,
                base_url=settings.ollama_base_url,
                temperature=temperature,
            )
        except Exception as exc:
            raise LLMGenerationError(
                f"Failed to initialize ChatOllama for model '{model_name}': {exc}"
            ) from exc

        _chat_model_cache[cache_key] = chat_model
        logger.info(
            f"Initialized ChatOllama client for model='{model_name}', "
            f"temperature={temperature}, base_url='{settings.ollama_base_url}'."
        )

    return _chat_model_cache[cache_key]


def check_ollama_connection(timeout_seconds: float = 3.0) -> bool:
    """
    Checks whether the Ollama daemon is reachable.

    Deliberately NOT called automatically inside generation functions —
    it's a separate, explicit health-check callers can use (e.g., a
    future Settings page connection-status indicator) without adding
    network latency to every chat turn.

    Args:
        timeout_seconds: Max time to wait for a response.

    Returns:
        True if Ollama responds successfully, False otherwise (including
        on any network error — this function never raises).
    """
    try:
        response = requests.get(
            f"{settings.ollama_base_url}/api/tags",
            timeout=timeout_seconds,
        )
        return response.status_code == 200
    except requests.RequestException as exc:
        logger.debug(f"Ollama connection check failed: {exc}")
        return False


def list_local_models(timeout_seconds: float = 3.0) -> list[str]:
    """
    Returns the list of model tags currently pulled/available in the
    local Ollama installation.

    Args:
        timeout_seconds: Max time to wait for a response.

    Returns:
        A list of model names (e.g., ["llama3:latest", "gemma3:latest"]).

    Raises:
        LLMGenerationError: If Ollama is unreachable or returns an
                unexpected response — unlike check_ollama_connection(),
                this function is used where the caller genuinely needs
                the list and should be told clearly why it's unavailable.
    """
    try:
        response = requests.get(
            f"{settings.ollama_base_url}/api/tags",
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise LLMGenerationError(
            f"Could not reach Ollama at '{settings.ollama_base_url}'. "
            f"Is the Ollama daemon running? Original error: {exc}"
        ) from exc

    return [model.get("name", "") for model in data.get("models", [])]


def clear_chat_model_cache() -> None:
    """
    Clears the cached ChatOllama instance(s).

    Used by tests to guarantee isolation, and available for a future
    "switch model at runtime" feature without restarting the process.
    """
    with _cache_lock:
        _chat_model_cache.clear()
    logger.debug("ChatOllama model cache cleared.")