"""
Test suite for the LLM service (Module 7).

Two test tiers:
  1. Unit tests (majority) — mock the ChatOllama layer entirely via
     monkeypatching app.infrastructure.ollama_client.get_chat_model, so
     model_registry, prompt_templates, and llm_service business logic
     are verified WITHOUT requiring a real Ollama daemon. This is what
     makes this suite runnable in CI/sandboxed environments.
  2. One integration test, explicitly gated on a real Ollama connection
     via check_ollama_connection() — automatically skipped (not failed)
     if Ollama isn't running locally.
"""

import pytest
from langchain_core.messages import AIMessage

from app.services.llm import (
    SUPPORTED_MODELS,
    is_supported_model,
    resolve_model_name,
    get_fallback_model,
    create_chat_prompt,
    GENERAL_CHAT_PROMPT_TEMPLATE,
    RAG_QA_PROMPT_TEMPLATE,
    generate_response,
    generate_from_template,
)
from app.infrastructure.ollama_client import (
    clear_chat_model_cache,
    check_ollama_connection,
)
from app.utils.exceptions import LLMGenerationError


# --- Fake ChatOllama for unit-testing llm_service without a real daemon ---

class _FakeChatModel:
    """Mimics ChatOllama's .invoke() interface for isolated unit tests."""

    def __init__(self, response_text: str = "This is a mocked response."):
        self.response_text = response_text
        self.last_messages = None

    def invoke(self, messages):
        self.last_messages = messages
        return AIMessage(content=self.response_text)


class _FailingChatModel:
    """Simulates an unreachable Ollama daemon or missing model."""

    def invoke(self, messages):
        raise ConnectionError("Simulated: could not connect to Ollama.")


@pytest.fixture(autouse=True)
def reset_model_cache():
    clear_chat_model_cache()
    yield
    clear_chat_model_cache()


# --- model_registry tests ---

def test_supported_models_contains_expected_entries() -> None:
    assert "llama3" in SUPPORTED_MODELS
    assert "gemma3" in SUPPORTED_MODELS


def test_is_supported_model_true_and_false_cases() -> None:
    assert is_supported_model("llama3") is True
    assert is_supported_model("gpt-4") is False


def test_resolve_model_name_with_explicit_valid_model() -> None:
    assert resolve_model_name("gemma3") == "gemma3"


def test_resolve_model_name_with_none_uses_configured_default() -> None:
    from config.settings import settings
    assert resolve_model_name(None) == settings.default_llm_model


def test_resolve_model_name_rejects_unsupported_model() -> None:
    with pytest.raises(LLMGenerationError):
        resolve_model_name("not-a-real-model")


def test_get_fallback_model_returns_supported_model() -> None:
    fallback = get_fallback_model()
    assert is_supported_model(fallback)


# --- prompt_templates tests ---

def test_create_chat_prompt_builds_two_message_template() -> None:
    template = create_chat_prompt("You are a bot.", "Answer: {question}")
    messages = template.format_messages(question="What is DNA?")
    assert len(messages) == 2
    assert messages[0].type == "system"
    assert messages[1].type == "human"
    assert "What is DNA?" in messages[1].content


def test_create_chat_prompt_rejects_empty_system_prompt() -> None:
    with pytest.raises(LLMGenerationError):
        create_chat_prompt("", "{question}")


def test_create_chat_prompt_rejects_empty_human_template() -> None:
    with pytest.raises(LLMGenerationError):
        create_chat_prompt("You are a bot.", "")


def test_general_chat_prompt_template_formats_correctly() -> None:
    messages = GENERAL_CHAT_PROMPT_TEMPLATE.format_messages(question="What is a ribosome?")
    assert "What is a ribosome?" in messages[-1].content


def test_rag_qa_prompt_template_requires_context_and_question() -> None:
    messages = RAG_QA_PROMPT_TEMPLATE.format_messages(
        context="The ribosome synthesizes proteins.",
        question="What does a ribosome do?",
    )
    rendered = messages[-1].content
    assert "The ribosome synthesizes proteins." in rendered
    assert "What does a ribosome do?" in rendered


def test_rag_qa_prompt_template_missing_variable_raises() -> None:
    with pytest.raises(KeyError):
        RAG_QA_PROMPT_TEMPLATE.format_messages(question="Missing context variable")


# --- llm_service tests (fully mocked, no real Ollama needed) ---

def test_generate_response_returns_llm_response(monkeypatch) -> None:
    fake_model = _FakeChatModel("The mitochondria is the powerhouse of the cell.")
    monkeypatch.setattr(
        "app.services.llm.llm_service.get_chat_model",
        lambda model_name, temperature: fake_model,
    )

    response = generate_response("What is the mitochondria?", model_name="llama3")

    assert response.content == "The mitochondria is the powerhouse of the cell."
    assert response.model_name == "llama3"
    assert response.prompt == "What is the mitochondria?"
    assert response.generation_time_ms >= 0


def test_generate_response_empty_prompt_raises() -> None:
    with pytest.raises(LLMGenerationError):
        generate_response("   ")


def test_generate_response_invalid_model_raises() -> None:
    with pytest.raises(LLMGenerationError):
        generate_response("A valid question", model_name="not-a-real-model")


def test_generate_response_wraps_connection_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.llm.llm_service.get_chat_model",
        lambda model_name, temperature: _FailingChatModel(),
    )

    with pytest.raises(LLMGenerationError, match="Generation failed"):
        generate_response("A valid question", model_name="llama3")


def test_generate_response_uses_custom_system_prompt(monkeypatch) -> None:
    fake_model = _FakeChatModel("Custom response.")
    monkeypatch.setattr(
        "app.services.llm.llm_service.get_chat_model",
        lambda model_name, temperature: fake_model,
    )

    generate_response(
        "Question here",
        model_name="llama3",
        system_prompt="You are a pirate.",
    )

    system_message = fake_model.last_messages[0]
    assert system_message.content == "You are a pirate."


def test_generate_from_template_formats_and_invokes(monkeypatch) -> None:
    fake_model = _FakeChatModel("BRCA1 is involved in DNA repair.")
    monkeypatch.setattr(
        "app.services.llm.llm_service.get_chat_model",
        lambda model_name, temperature: fake_model,
    )

    response = generate_from_template(
        RAG_QA_PROMPT_TEMPLATE,
        variables={
            "context": "BRCA1 is a tumor suppressor gene involved in DNA repair.",
            "question": "What does BRCA1 do?",
        },
        model_name="gemma3",
    )

    assert response.content == "BRCA1 is involved in DNA repair."
    assert response.model_name == "gemma3"
    assert "What does BRCA1 do?" in response.prompt


def test_generate_from_template_missing_variable_raises(monkeypatch) -> None:
    fake_model = _FakeChatModel("Should not be reached.")
    monkeypatch.setattr(
        "app.services.llm.llm_service.get_chat_model",
        lambda model_name, temperature: fake_model,
    )

    with pytest.raises(LLMGenerationError, match="missing a required variable"):
        generate_from_template(
            RAG_QA_PROMPT_TEMPLATE,
            variables={"question": "Missing context"},
            model_name="llama3",
        )


# --- Real Ollama integration test (auto-skipped if unavailable) ---

@pytest.mark.skipif(
    not check_ollama_connection(),
    reason="Ollama daemon not reachable at configured base_url — skipping live integration test.",
)
def test_integration_real_ollama_generation() -> None:
    """
    Exercises the real Ollama daemon end-to-end. Requires `ollama serve`
    running locally with the default model pulled. Automatically skips
    (not fails) in environments without Ollama installed, e.g., CI.
    """
    response = generate_response("In one sentence, what is a gene?")
    assert isinstance(response.content, str)
    assert len(response.content.strip()) > 0
    assert response.generation_time_ms > 0