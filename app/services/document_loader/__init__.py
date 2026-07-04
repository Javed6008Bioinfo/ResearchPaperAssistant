"""
Public API for the document_loader service package.

Other modules (e.g., the future UI integration, or Module 4's chunking
service) should import from this package root rather than reaching into
individual loader files directly.
"""

from app.services.document_loader.schemas import LoadedDocument
from app.services.document_loader.loader_factory import load_document, get_loader
from app.services.document_loader.file_storage import save_uploaded_file

__all__ = [
    "LoadedDocument",
    "load_document",
    "get_loader",
    "save_uploaded_file",
]