"""
File storage utility for persisting uploaded documents to disk.

Separated from the loaders themselves because "where a file is stored"
is a different responsibility from "how a file's text is extracted."
The Streamlit upload UI (Module 2) currently holds files only in memory
(st.file_uploader gives an in-memory buffer) — this module provides the
function that will save that buffer to data/raw_uploads/ once we wire
the UI to real processing.
"""

import uuid
from pathlib import Path

from config.constants import RAW_UPLOADS_DIR, SUPPORTED_FILE_EXTENSIONS
from app.utils.exceptions import UnsupportedFileTypeError
from app.utils.logger import logger


def save_uploaded_file(file_bytes: bytes, original_filename: str) -> Path:
    """
    Saves uploaded file bytes to data/raw_uploads/ with a collision-safe
    unique filename, while preserving the original name for display purposes.

    Args:
        file_bytes: Raw file content.
        original_filename: The filename as provided by the user (used only
                            to validate extension and build a readable
                            stored filename — never trusted as a path).

    Returns:
        The absolute Path to the saved file on disk.

    Raises:
        UnsupportedFileTypeError: If the file extension isn't supported.
    """
    original_path = Path(original_filename)
    extension = original_path.suffix.lower()

    if extension not in SUPPORTED_FILE_EXTENSIONS:
        raise UnsupportedFileTypeError(
            f"Cannot save unsupported file type '{extension}'. "
            f"Supported types: {', '.join(SUPPORTED_FILE_EXTENSIONS)}"
        )

    RAW_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    # Prefix with a short UUID to avoid overwriting files with identical
    # names uploaded by different users/sessions, while keeping the
    # original stem readable for debugging in the filesystem.
    safe_stem = original_path.stem.replace(" ", "_")
    unique_filename = f"{uuid.uuid4().hex[:8]}_{safe_stem}{extension}"
    destination_path = RAW_UPLOADS_DIR / unique_filename

    destination_path.write_bytes(file_bytes)
    logger.info(f"Saved uploaded file '{original_filename}' -> '{destination_path}'")

    return destination_path