"""
Static, non-secret constants used across the application.

These values do not change between environments (dev/staging/prod)
and therefore do not belong in environment variables. Values that DO
vary by environment (API keys, hosts, ports) belong in config/settings.py.
"""

from pathlib import Path

# --- Project root resolution ---
# Resolves to the project root regardless of where a script is invoked from.
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

# --- Directory paths ---
DATA_DIR: Path = PROJECT_ROOT / "data"
RAW_UPLOADS_DIR: Path = DATA_DIR / "raw_uploads"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
VECTOR_STORE_DIR: Path = DATA_DIR / "vector_store"
LOGS_DIR: Path = PROJECT_ROOT / "logs"

# --- Supported document formats (Module 3) ---
SUPPORTED_FILE_EXTENSIONS: tuple[str, ...] = (".pdf", ".docx", ".txt")

# --- Application metadata ---
APP_NAME: str = "Research Paper Assistant"
APP_VERSION: str = "0.1.0"