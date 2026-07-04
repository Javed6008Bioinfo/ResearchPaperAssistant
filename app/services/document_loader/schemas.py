"""
Shared data contract for all document loaders.

Every loader (PDF, DOCX, TXT — and any future format) must return a
LoadedDocument. This is the single interface that Module 4 (Text
Chunking) and beyond will consume, so the rest of the pipeline never
needs to know which file format the original document was.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LoadedDocument:
    """
    Normalized representation of a loaded document, regardless of
    original file format.

    Attributes:
        filename: Original filename as uploaded by the user.
        file_type: Normalized type, one of "pdf", "docx", "txt".
        full_text: Complete extracted text, concatenated across pages/sections.
        pages: Text split by logical page/section. For PDFs this is one
               entry per PDF page. For DOCX/TXT (which have no fixed
               pagination) this is a single-entry list containing the
               full text, unless the format has natural sections.
        page_count: Number of entries in `pages`. Kept as an explicit
               field (rather than always calling len(pages)) so it can be
               displayed in the UI without recomputation, and so future
               formats can report a "logical" page count that differs
               from len(pages) if needed.
        metadata: Extra format-specific metadata (e.g., PDF author/title,
               DOCX core properties). Free-form dict so each loader can
               attach what's relevant without changing this schema.
    """

    filename: str
    file_type: str
    full_text: str
    pages: list[str]
    page_count: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_empty(self) -> bool:
        """Returns True if no meaningful text was extracted."""
        return len(self.full_text.strip()) == 0