"""
Loader dispatch and validation entry point.

This is the ONLY file outside this package that other modules should
import from. It hides which concrete loader class handles which
extension, validates input before attempting extraction, and centralizes
logging for the whole document-loading flow.
"""

from pathlib import Path

from app.services.document_loader.base_loader import BaseDocumentLoader
from app.services.document_loader.docx_loader import DOCXLoader
from app.services.document_loader.pdf_loader import PDFLoader
from app.services.document_loader.schemas import LoadedDocument
from app.services.document_loader.txt_loader import TXTLoader
from app.utils.exceptions import DocumentParsingError, UnsupportedFileTypeError
from app.utils.logger import logger

# Registry mapping file extensions to loader classes.
# Adding a new format later = one new loader class + one new entry here.
_LOADER_REGISTRY: dict[str, type[BaseDocumentLoader]] = {
    ".pdf": PDFLoader,
    ".docx": DOCXLoader,
    ".txt": TXTLoader,
}


def get_loader(file_path: Path) -> BaseDocumentLoader:
    """
    Returns the appropriate loader instance for the given file's extension.

    Raises:
        UnsupportedFileTypeError: If the extension isn't registered.
    """
    extension = file_path.suffix.lower()
    loader_class = _LOADER_REGISTRY.get(extension)

    if loader_class is None:
        supported = ", ".join(_LOADER_REGISTRY.keys())
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{extension}' for '{file_path.name}'. "
            f"Supported types: {supported}"
        )

    return loader_class()


def load_document(file_path: Path) -> LoadedDocument:
    """
    Main entry point for document loading: validates the file exists,
    selects the correct loader, and returns a normalized LoadedDocument.

    Args:
        file_path: Absolute path to a file already saved on disk
                    (see file_storage.py for saving uploaded bytes first).

    Returns:
        LoadedDocument with extracted text and metadata.

    Raises:
        UnsupportedFileTypeError: Unknown file extension.
        DocumentParsingError: File is missing, empty, or fails to parse.
    """
    if not file_path.exists():
        raise DocumentParsingError(f"File not found: {file_path}")

    if file_path.stat().st_size == 0:
        raise DocumentParsingError(f"File '{file_path.name}' is empty (0 bytes).")

    logger.info(f"Loading document: {file_path.name}")
    loader = get_loader(file_path)

    try:
        document = loader.load(file_path)
    except (UnsupportedFileTypeError, DocumentParsingError):
        raise
    except Exception as exc:
        # Catch-all safety net: never let an unexpected library error
        # surface as a raw traceback to calling code (e.g., the UI layer).
        raise DocumentParsingError(
            f"Unexpected error while parsing '{file_path.name}': {exc}"
        ) from exc

    logger.info(
        f"Loaded '{file_path.name}' — {document.page_count} page(s), "
        f"{len(document.full_text)} characters extracted."
    )
    return document