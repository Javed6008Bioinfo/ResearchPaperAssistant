"""
Centralized Streamlit session state schema.

Every key used anywhere in the UI is defined and defaulted here. This is
the single source of truth for shared application state. Future modules
(document loading, RAG pipeline, chat) will READ and WRITE these same
keys instead of introducing new ad hoc state scattered across files.

Design principle: no page or component should call `st.session_state["x"]`
with a raw string literal for a NEW key — add it here first, so the whole
state schema stays discoverable in one file.
"""

from typing import Any
import streamlit as st


def _default_state() -> dict[str, Any]:
    """
    Returns the default shape of session state.

    NOTE: Values here are placeholders / empty containers only.
    Real data population starts in Module 3 (uploads) and Module 9 (chat).
    """
    return {
        # --- Navigation ---
        "active_page": "Home",

        # --- Uploaded papers (populated in Module 3) ---
        # Each entry will eventually look like:
        # {"id": str, "filename": str, "upload_time": str,
        #  "status": "processed"|"processing"|"failed", "pages": int}
        "uploaded_papers": [],

        # --- Currently selected paper for chat / info panel ---
        "active_paper_id": None,

        # --- Chat history (populated in Module 9) ---
        # Each entry: {"role": "user"|"assistant", "content": str, "sources": list}
        "chat_history": [],

        # --- Settings (defaults mirror config/settings.py; wired in Module 7) ---
        "selected_llm_model": "llama3",
        "chunk_size": 1000,
        "chunk_overlap": 150,
        "retrieval_top_k": 4,

        # --- UI flags ---
        "sidebar_upload_expanded": True,
    }


def init_session_state() -> None:
    """
    Initialize all session state keys with defaults if not already set.

    Must be called once at the top of app/main.py before any page renders.
    Safe to call on every rerun — only missing keys are set.
    """
    defaults = _default_state()
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_active_paper() -> dict[str, Any] | None:
    """
    Convenience accessor: returns the currently active paper's metadata dict,
    or None if no paper is selected/uploaded yet.

    Centralizing this lookup avoids repeating the same filter logic in
    every page/component that needs to know "which paper are we looking at".
    """
    active_id = st.session_state.get("active_paper_id")
    if not active_id:
        return None

    for paper in st.session_state.get("uploaded_papers", []):
        if paper["id"] == active_id:
            return paper
    return None