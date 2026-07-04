"""
Custom exception hierarchy for the Research Paper Assistant.

Using specific exception types (instead of generic Exception/ValueError)
lets calling code, and the Streamlit UI, handle failures precisely
(e.g., show a friendly message for UnsupportedFileTypeError vs. a stack
trace for an unexpected bug).
"""


class ResearchAssistantError(Exception):
    """Base exception for all application-specific errors."""


class UnsupportedFileTypeError(ResearchAssistantError):
    """Raised when a user uploads a file type that isn't supported (Module 3)."""


class DocumentParsingError(ResearchAssistantError):
    """Raised when a document fails to parse or extract text (Module 3)."""


class TextChunkingError(ResearchAssistantError):
    """Raised when text chunking fails or receives invalid parameters (Module 4)."""


class EmbeddingGenerationError(ResearchAssistantError):
    """Raised when embedding generation fails (Module 5)."""


class VectorStoreError(ResearchAssistantError):
    """Raised for ChromaDB read/write failures (Module 6)."""


class LLMGenerationError(ResearchAssistantError):
    """Raised when the Ollama LLM fails to generate a response (Module 7)."""


class RAGPipelineError(ResearchAssistantError):
    """Raised when the retrieval-augmented generation pipeline fails (Module 8)."""


# """
# Custom exception hierarchy for the Research Paper Assistant.

# Using specific exception types (instead of generic Exception/ValueError)
# lets calling code, and the Streamlit UI, handle failures precisely
# (e.g., show a friendly message for UnsupportedFileTypeError vs. a stack
# trace for an unexpected bug).
# """


# class ResearchAssistantError(Exception):
#     """Base exception for all application-specific errors."""


# class UnsupportedFileTypeError(ResearchAssistantError):
#     """Raised when a user uploads a file type that isn't supported (Module 3)."""


# class DocumentParsingError(ResearchAssistantError):
#     """Raised when a document fails to parse or extract text (Module 3)."""


# class EmbeddingGenerationError(ResearchAssistantError):
#     """Raised when embedding generation fails (Module 5)."""


# class VectorStoreError(ResearchAssistantError):
#     """Raised for ChromaDB read/write failures (Module 6)."""


# class LLMGenerationError(ResearchAssistantError):
#     """Raised when the Ollama LLM fails to generate a response (Module 7)."""


# class RAGPipelineError(ResearchAssistantError):
#     """Raised when the retrieval-augmented generation pipeline fails (Module 8)."""