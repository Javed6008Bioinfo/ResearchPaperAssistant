"""
Abstract base class defining the contract every document loader must
implement. This is the "strategy" interface in the Strategy pattern —
loader_factory.py depends on this abstraction, never on concrete loaders
directly, so new formats can be added without modifying dispatch logic.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from app.services.document_loader.schemas import LoadedDocument


class BaseDocumentLoader(ABC):
    """Common interface for all document loaders."""

    @abstractmethod
    def load(self, file_path: Path) -> LoadedDocument:
        """
        Extract text and metadata from the file at `file_path`.

        Args:
            file_path: Absolute path to the file on disk.

        Returns:
            A populated LoadedDocument.

        Raises:
            DocumentParsingError: If the file cannot be read or parsed.
        """
        raise NotImplementedError