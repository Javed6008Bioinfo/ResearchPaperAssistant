"""
Public API for the llm service package.

Module 8 (RAG Pipeline) and beyond should import from this package
root rather than reaching into individual files.
"""

from app.services.llm.schemas import LLMResponse
from app.services.llm.llm_service import generate_response, generate_from_template
from app.services.llm.model_registry import (
    SUPPORTED_MODELS,
    is_supported_model,
    resolve_model_name,
    get_fallback_model,
)
from app.services.llm.prompt_templates import (
    create_chat_prompt,
    DEFAULT_SYSTEM_PROMPT,
    GENERAL_CHAT_PROMPT_TEMPLATE,
    RAG_QA_PROMPT_TEMPLATE,
)

__all__ = [
    "LLMResponse",
    "generate_response",
    "generate_from_template",
    "SUPPORTED_MODELS",
    "is_supported_model",
    "resolve_model_name",
    "get_fallback_model",
    "create_chat_prompt",
    "DEFAULT_SYSTEM_PROMPT",
    "GENERAL_CHAT_PROMPT_TEMPLATE",
    "RAG_QA_PROMPT_TEMPLATE",
]