"""
Shared data contract for the LLM service.

LLMResponse is the output of Module 7's generation functions and will
be the input to Module 8's answer-assembly step and Module 9's chat
history storage.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class LLMResponse:
    """
    Result of a single LLM generation call.

    Attributes:
        content: The generated text response.
        model_name: Which Ollama model produced this response — stored
                per-response (not just read from global config) so chat
                history (Module 9) can display which model answered
                each turn, even if the user switches models mid-session.
        prompt: The final rendered prompt/question sent to the model
                (post-template-formatting), kept for debugging and for
                potential display in a future "view prompt" debug panel.
        generation_time_ms: Wall-clock generation latency, for
                performance visibility (Module 17 logging/monitoring).
        metadata: Reserved for future fields (e.g., token counts, if
                Ollama's response metadata is later parsed for them)
                without requiring a schema change.

    frozen=True: an LLM response is a completed, immutable result — a
    future accidental in-place mutation (e.g., partially editing
    .content) should be an error, not something that silently corrupts
    chat history.
    """

    content: str
    model_name: str
    prompt: str
    generation_time_ms: float
    metadata: dict[str, Any] = field(default_factory=dict)