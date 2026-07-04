"""
Plain text document loader.

Handles encoding gracefully: research papers exported as .txt from
different tools/OSes are not always UTF-8. We attempt UTF-8 first,
then fall back to latin-1 (which never raises on arbitrary byte
sequences) rather than crashing the whole upload on an encoding quirk.
"""

from pathlib import Path

from app.services.document_loader.base_loader import BaseDocumentLoader
from app.services.document_loader.schemas import LoadedDocument
from app.utils.exceptions import DocumentParsingError
from app.utils.logger import logger


class TXTLoader(BaseDocumentLoader):
    """Extracts text from plain .txt files with encoding fallback."""

    _ENCODING_ATTEMPTS: tuple[str, ...] = ("utf-8", "latin-1")

    def load(self, file_path: Path) -> LoadedDocument:
        raw_bytes = self._read_bytes(file_path)
        text = self._decode(raw_bytes, file_path.name)

        full_text = text.strip()

        document = LoadedDocument(
            filename=file_path.name,
            file_type="txt",
            full_text=full_text,
            pages=[full_text],  # plain text has no pagination concept
            page_count=1,
            metadata={},
        )

        if document.is_empty():
            logger.warning(f"TXT file '{file_path.name}' is empty.")

        return document

    @staticmethod
    def _read_bytes(file_path: Path) -> bytes:
        try:
            return file_path.read_bytes()
        except OSError as exc:
            raise DocumentParsingError(
                f"Failed to read TXT file '{file_path.name}': {exc}"
            ) from exc

    def _decode(self, raw_bytes: bytes, filename: str) -> str:
        for encoding in self._ENCODING_ATTEMPTS:
            try:
                return raw_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue
        raise DocumentParsingError(
            f"Could not decode TXT file '{filename}' with supported encodings "
            f"{self._ENCODING_ATTEMPTS}."
        )