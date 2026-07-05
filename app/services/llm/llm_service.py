"""
Orchestration layer for LLM text generation via Ollama.

This is the main entry point other modules should import from. It
resolves/validates the requested model, builds the appropriate message
sequence, invokes the cached ChatOllama client, times the call, and
returns a typed LLMResponse — no other module needs to know about
langchain_core message types or ChatOllama's invoke() signature.
"""

import time

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from app.infrastructure.ollama_client import get_chat_model
from app.services.llm.model_registry import resolve_model_name
from app.services.llm.prompt_templates import DEFAULT_SYSTEM_PROMPT
from app.services.llm.schemas import LLMResponse
from app.utils.exceptions import LLMGenerationError
from app.utils.logger import logger

DEFAULT_TEMPERATURE_FALLBACK = 0.2  # used only if settings/temperature is somehow unset


def generate_response(
    prompt: str,
    model_name: str | None = None,
    temperature: float | None = None,
    system_prompt: str | None = None,
) -> LLMResponse:
    """
    Generates a single LLM response for a raw prompt string.

    Args:
        prompt: The user's question/instruction text. Must be non-empty.
        model_name: Optional model override. Defaults to
                config/settings.py's configured default model.
        temperature: Optional sampling temperature override. Defaults
                to config/settings.py's configured value.
        system_prompt: Optional system-role instruction override.
                Defaults to prompt_templates.DEFAULT_SYSTEM_PROMPT.

    Returns:
        A populated LLMResponse.

    Raises:
        LLMGenerationError: If prompt is empty, the model name is
                unsupported, or generation fails (e.g., Ollama
                unreachable, model not pulled locally).
    """
    if not prompt or not prompt.strip():
        raise LLMGenerationError("Cannot generate a response for an empty prompt.")

    from config.settings import settings  # local import avoids a hard
    # module-load-time dependency on settings for callers that only
    # need generate_from_template with fully-explicit arguments.

    resolved_model = resolve_model_name(model_name)
    resolved_temperature = temperature if temperature is not None else settings.llm_temperature
    resolved_system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT

    chat_model = get_chat_model(resolved_model, resolved_temperature)

    messages = [
        SystemMessage(content=resolved_system_prompt),
        HumanMessage(content=prompt),
    ]

    start_time = time.perf_counter()
    try:
        result = chat_model.invoke(messages)
    except Exception as exc:
        raise LLMGenerationError(
            f"Generation failed using model '{resolved_model}'. "
            f"Confirm Ollama is running and the model is pulled "
            f"(`ollama pull {resolved_model}`). Original error: {exc}"
        ) from exc
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    logger.info(
        f"Generated response using model='{resolved_model}' "
        f"in {elapsed_ms:.0f}ms ({len(result.content)} chars)."
    )

    return LLMResponse(
        content=result.content,
        model_name=resolved_model,
        prompt=prompt,
        generation_time_ms=elapsed_ms,
    )


def generate_from_template(
    template: ChatPromptTemplate,
    variables: dict[str, str],
    model_name: str | None = None,
    temperature: float | None = None,
) -> LLMResponse:
    """
    Generates a single LLM response by formatting a ChatPromptTemplate
    with the given variables, then invoking the model.

    This is the function Module 8's RAG pipeline will call with
    prompt_templates.RAG_QA_PROMPT_TEMPLATE and
    {"context": ..., "question": ...}.

    Args:
        template: A ChatPromptTemplate (see prompt_templates.py).
        variables: Values to fill the template's placeholders. Missing
                required variables raise a clear error rather than a
                cryptic KeyError from deep inside langchain_core.
        model_name: Optional model override.
        temperature: Optional sampling temperature override.

    Returns:
        A populated LLMResponse. Its `.prompt` field contains the
        fully-rendered human-message text (post-formatting), not the
        raw template string, for accurate debugging.

    Raises:
        LLMGenerationError: If template formatting fails (e.g., a
                required variable is missing) or generation fails.
    """
    from config.settings import settings

    resolved_model = resolve_model_name(model_name)
    resolved_temperature = temperature if temperature is not None else settings.llm_temperature

    try:
        formatted_messages = template.format_messages(**variables)
    except KeyError as exc:
        raise LLMGenerationError(
            f"Prompt template is missing a required variable: {exc}"
        ) from exc
    except Exception as exc:
        raise LLMGenerationError(f"Failed to format prompt template: {exc}") from exc

    chat_model = get_chat_model(resolved_model, resolved_temperature)

    start_time = time.perf_counter()
    try:
        result = chat_model.invoke(formatted_messages)
    except Exception as exc:
        raise LLMGenerationError(
            f"Generation failed using model '{resolved_model}'. "
            f"Confirm Ollama is running and the model is pulled "
            f"(`ollama pull {resolved_model}`). Original error: {exc}"
        ) from exc
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    # Reconstruct a readable "final prompt" string for the response
    # record, using whichever message carries the user-facing content.
    rendered_prompt = "\n".join(
        f"[{message.type}] {message.content}" for message in formatted_messages
    )

    logger.info(
        f"Generated templated response using model='{resolved_model}' "
        f"in {elapsed_ms:.0f}ms ({len(result.content)} chars)."
    )

    return LLMResponse(
        content=result.content,
        model_name=resolved_model,
        prompt=rendered_prompt,
        generation_time_ms=elapsed_ms,
    )