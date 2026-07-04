"""
Settings page — user-configurable parameters for the RAG pipeline.

IMPORTANT: Changing values here only updates st.session_state in this
module. Wiring these settings into actual embedding/chunking/LLM
behavior happens in Modules 4, 5, and 7 respectively.
"""

import streamlit as st


_AVAILABLE_MODELS: list[str] = ["llama3", "gemma3"]


def render_settings_page() -> None:
    """Render the Settings page: model selection and pipeline parameters."""
    st.header("⚙️ Settings")
    st.caption("Configure the AI models and retrieval parameters used across the app.")

    st.subheader("🧠 Language Model")
    selected_model = st.selectbox(
        "Active LLM (via Ollama)",
        options=_AVAILABLE_MODELS,
        index=_AVAILABLE_MODELS.index(st.session_state["selected_llm_model"]),
        help="Requires the corresponding model to be pulled locally in Ollama.",
    )
    st.session_state["selected_llm_model"] = selected_model

    st.divider()

    st.subheader("✂️ Text Chunking")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state["chunk_size"] = st.slider(
            "Chunk Size (characters)", min_value=200, max_value=2000,
            value=st.session_state["chunk_size"], step=50,
        )
    with col2:
        st.session_state["chunk_overlap"] = st.slider(
            "Chunk Overlap (characters)", min_value=0, max_value=500,
            value=st.session_state["chunk_overlap"], step=10,
        )

    st.divider()

    st.subheader("🔍 Retrieval")
    st.session_state["retrieval_top_k"] = st.slider(
        "Number of chunks retrieved per query (Top-K)",
        min_value=1, max_value=10,
        value=st.session_state["retrieval_top_k"],
    )

    st.divider()
    st.info(
        "ℹ️ These settings define parameters for future modules "
        "(chunking, embeddings, and LLM generation). They are not yet "
        "connected to backend processing."
    )