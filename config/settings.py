"""
Centralized, environment-driven application settings.

All values that may differ between local development, Hugging Face Spaces,
and Render deployments live here. Settings are loaded from environment
variables (via a .env file locally) and validated at startup using Pydantic,
so misconfiguration fails fast with a clear error instead of silently
breaking a later module.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from config.constants import (
    RAW_UPLOADS_DIR,
    PROCESSED_DATA_DIR,
    VECTOR_STORE_DIR,
    LOGS_DIR,
)


class Settings(BaseSettings):
    """Typed application settings, populated from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Environment ---
    environment: str = "development"  # development | staging | production
    debug: bool = True

    # --- Ollama / LLM configuration (used from Module 7 onward) ---
    ollama_base_url: str = "http://localhost:11434"
    default_llm_model: str = "llama3"
    fallback_llm_model: str = "gemma3"
    llm_temperature: float = 0.2

    # --- Embeddings (Module 5) ---
    embedding_model_name: str = "all-MiniLM-L6-v2"

    # --- Vector store (Module 6) ---
    chroma_persist_directory: str = str(VECTOR_STORE_DIR)
    chroma_collection_name: str = "research_papers"

    # --- Chunking (Module 4) ---
    chunk_size: int = 1000
    chunk_overlap: int = 150

    # --- File handling (Module 3) ---
    max_upload_size_mb: int = 50
    raw_uploads_directory: str = str(RAW_UPLOADS_DIR)
    processed_data_directory: str = str(PROCESSED_DATA_DIR)

    # --- Logging ---
    log_level: str = "INFO"
    logs_directory: str = str(LOGS_DIR)


def get_settings() -> Settings:
    """
    Factory function for Settings.

    Using a factory (instead of a bare module-level instance) makes it
    trivial to mock/override settings in unit tests.
    """
    return Settings()


# Singleton instance used throughout the application
settings = get_settings()