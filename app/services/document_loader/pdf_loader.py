"""
PDF document loader using pypdf.

pypdf is the actively maintained successor to the deprecated PyPDF2
package. We use it directly (no wrapper library) to keep the dependency
surface small and avoid abstraction layers that hide extraction errors.
"""

from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.services.document_loader.base_loader import BaseDocumentLoader
from app.services.document_loader.schemas import LoadedDocument
from app.utils.exceptions import DocumentParsingError
from app.utils.logger import logger


class PDFLoader(BaseDocumentLoader):
    """Extracts text and per-page content from PDF files."""

    def load(self, file_path: Path) -> LoadedDocument:
        try:
            reader = PdfReader(str(file_path))
        except (PdfReadError, FileNotFoundError, OSError) as exc:
            raise DocumentParsingError(
                f"Failed to open PDF '{file_path.name}': {exc}"
            ) from exc

        if reader.is_encrypted:
            raise DocumentParsingError(
                f"PDF '{file_path.name}' is password-protected and cannot be processed."
            )

        pages: list[str] = []
        for page_number, page in enumerate(reader.pages, start=1):
            try:
                page_text = page.extract_text() or ""
            except Exception as exc:
                # A single corrupted page shouldn't fail the whole document —
                # log and continue with an empty page rather than raising.
                logger.warning(
                    f"Could not extract text from page {page_number} of "
                    f"'{file_path.name}': {exc}"
                )
                page_text = ""
            pages.append(page_text.strip())

        full_text = "\n\n".join(pages).strip()

        metadata = {}
        if reader.metadata:
            metadata = {
                "title": reader.metadata.title or "",
                "author": reader.metadata.author or "",
                "creator": reader.metadata.creator or "",
            }

        document = LoadedDocument(
            filename=file_path.name,
            file_type="pdf",
            full_text=full_text,
            pages=pages,
            page_count=len(pages),
            metadata=metadata,
        )

        if document.is_empty():
            logger.warning(
                f"PDF '{file_path.name}' produced no extractable text "
                "(likely a scanned/image-based PDF without OCR)."
            )

        return document