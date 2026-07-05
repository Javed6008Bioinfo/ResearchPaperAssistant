"""
Reusable prompt template construction for the LLM service.

This file has NO dependency on retrieval, chunking, or the vector store
— it only knows about langchain_core's prompt primitives. This keeps it
safely reusable by multiple future modules (Module 8's RAG pipeline,
Module 11's summarization, Module 12's citation extraction) without
risking circular imports back into services that depend on this one.

Templates defined here are inert data structures until a service module
calls .format_messages() on them and passes the result to the LLM —
no template in this file triggers any generation on its own.
"""

from langchain_core.prompts import ChatPromptTemplate

from app.utils.exceptions import LLMGenerationError

# The base persona/behavior instructions shared across most prompts in
# this app. Centralized here so tone/behavior stays consistent whether
# the user is chatting, requesting a summary, or extracting citations.
DEFAULT_SYSTEM_PROMPT: str = (
    "You are a knowledgeable research assistant specializing in "
    "bioinformatics and the life sciences. Answer clearly and precisely. "
    "If you are uncertain or the available information is insufficient, "
    "say so explicitly rather than guessing. Never fabricate citations, "
    "gene names, statistics, or study results that are not grounded in "
    "the information you were given."
)


def create_chat_prompt(system_prompt: str, human_template: str) -> ChatPromptTemplate:
    """
    Factory for a validated two-message (system + human) ChatPromptTemplate.

    Args:
        system_prompt: The system-role instruction text (persona,
                behavior constraints). May contain {variable} placeholders.
        human_template: The human-role message template. May contain
                {variable} placeholders (e.g., "{question}", "{context}").

    Returns:
        A ChatPromptTemplate ready for .format_messages(**variables).

    Raises:
        LLMGenerationError: If either template string is empty.
    """
    if not system_prompt or not system_prompt.strip():
        raise LLMGenerationError("system_prompt cannot be empty.")
    if not human_template or not human_template.strip():
        raise LLMGenerationError("human_template cannot be empty.")

    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_template),
    ])


# --- General-purpose chat template ---
# Used for plain question-answering without retrieved context (e.g., a
# general bioinformatics question unrelated to an uploaded paper).
GENERAL_CHAT_PROMPT_TEMPLATE: ChatPromptTemplate = create_chat_prompt(
    system_prompt=DEFAULT_SYSTEM_PROMPT,
    human_template="{question}",
)


# --- RAG question-answering template (reserved for Module 8) ---
# Defined now so all prompt engineering lives in one file from the
# start. NOT used by any code in this module — Module 8's retriever
# will populate {context} with formatted RetrievedChunk content and
# {question} with the user's message, then call llm_service with it.
RAG_QA_PROMPT_TEMPLATE: ChatPromptTemplate = create_chat_prompt(
    system_prompt=DEFAULT_SYSTEM_PROMPT,
    human_template=(
        "Answer the question using ONLY the context provided below, "
        "extracted from the user's uploaded research paper(s). "
        "If the answer cannot be found in the context, say so explicitly "
        "instead of guessing.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}"
    ),
)