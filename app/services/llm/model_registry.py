"""
Static registry of supported LLM models and fast, network-free validation.

Deliberately does NOT query Ollama's API to check what's actually pulled
locally — that would add network latency to every single generation call.
Use app.infrastructure.ollama_client.list_local_models() explicitly
(e.g., in a Settings/diagnostics UI) if you need to confirm a model is
actually installed, separately from this registry's fast validation.
"""

from config.settings import settings
from app.utils.exceptions import LLMGenerationError

# Maps the internal model identifier (used in config, session state, and
# code) to a human-readable display name. Mirrors the model choices
# already presented on the Module 2 Settings page, so this registry is
# the eventual single source of truth for that dropdown once wired up.
SUPPORTED_MODELS: dict[str, str] = {
    "llama3": "Llama 3",
    "gemma3": "Gemma 3",
}


def is_supported_model(model_name: str) -> bool:
    """Returns True if model_name is one of the app's supported models."""
    return model_name in SUPPORTED_MODELS


def resolve_model_name(requested_model: str | None) -> str:
    """
    Resolves and validates a requested model name.

    Args:
        requested_model: A model identifier, or None to use the
                configured default (config/settings.py's
                DEFAULT_LLM_MODEL).

    Returns:
        A validated model name guaranteed to be in SUPPORTED_MODELS.

    Raises:
        LLMGenerationError: If the resolved model name is not supported.
                Note: this validates against the app's known model
                registry, not against what's actually pulled in Ollama —
                an unpulled-but-supported model will fail later, at
                generation time, with a clearer Ollama-specific error.
    """
    resolved = requested_model or settings.default_llm_model

    if not is_supported_model(resolved):
        supported = ", ".join(SUPPORTED_MODELS.keys())
        raise LLMGenerationError(
            f"Unsupported model '{resolved}'. Supported models: {supported}"
        )

    return resolved


def get_fallback_model() -> str:
    """
    Returns the configured fallback model, validated against the registry.

    Used by callers that want to retry generation with a fallback model
    if the primary one fails (e.g., a future resilience layer in
    Module 8's RAG pipeline could catch LLMGenerationError and retry
    once with this fallback).
    """
    return resolve_model_name(settings.fallback_llm_model)