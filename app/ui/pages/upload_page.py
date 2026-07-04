"""
Upload page — UI for adding papers to the library.

IMPORTANT: This module contains NO real document processing. The
`_mock_process_upload` function simulates what Module 3 (Document
Loading) will implement for real: extracting text, page count, and
storing the file. It exists so the full UI/UX flow can be reviewed
and tested before any backend logic is written.
"""

import uuid
from datetime import datetime

import streamlit as st

from config.constants import SUPPORTED_FILE_EXTENSIONS
from app.ui.components.status_badge import render_status_badge


def _mock_process_upload(uploaded_file) -> dict:
    """
    PLACEHOLDER — simulates document processing.

    Module 3 will replace this with real logic:
        - save file to data/raw_uploads/
        - extract text via PyPDF / python-docx
        - extract page count and basic metadata

    Returns a paper metadata dict matching the session_state schema.
    """
    return {
        "id": str(uuid.uuid4()),
        "filename": uploaded_file.name,
        "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "processed",  # mocked; will be "processing" -> "processed"/"failed" for real
        "pages": "—",  # unknown until Module 3 extracts it
    }


def render_upload_page() -> None:
    """Render the Upload page: file uploader + upload history table."""
    st.header("📤 Upload Research Papers")
    st.caption(
        f"Supported formats: {', '.join(SUPPORTED_FILE_EXTENSIONS)}. "
        "Files are processed and indexed for chat and analysis."
    )

    uploaded_files = st.file_uploader(
        label="Drag and drop or browse files",
        type=[ext.lstrip(".") for ext in SUPPORTED_FILE_EXTENSIONS],
        accept_multiple_files=True,
        help="You can upload multiple papers at once.",
    )

    if uploaded_files:
        if st.button("Process Uploaded Files", type="primary"):
            with st.spinner("Processing papers..."):
                for file in uploaded_files:
                    # NOTE: real processing happens in Module 3.
                    paper_metadata = _mock_process_upload(file)
                    st.session_state["uploaded_papers"].append(paper_metadata)

                    # Auto-select the most recently uploaded paper as active
                    st.session_state["active_paper_id"] = paper_metadata["id"]
                    st.session_state["_active_paper_cache"] = paper_metadata

            st.success(f"✅ Processed {len(uploaded_files)} file(s).")
            st.rerun()

    st.divider()
    st.subheader("📚 Paper Library")

    papers = st.session_state.get("uploaded_papers", [])
    if not papers:
        st.info("No papers uploaded yet. Upload a file above to get started.")
        return

    for paper in papers:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"**{paper['filename']}**")
                st.caption(f"Uploaded: {paper['upload_time']}")
            with col2:
                render_status_badge(paper["status"])
            with col3:
                if st.button("Select", key=f"select_{paper['id']}", use_container_width=True):
                    st.session_state["active_paper_id"] = paper["id"]
                    st.session_state["_active_paper_cache"] = paper
                    st.rerun()