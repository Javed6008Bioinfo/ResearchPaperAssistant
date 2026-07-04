"""
Home page — landing view for the application.

Gives new users (bioinformatics students, researchers) an immediate
overview of what the tool does and its current status. Purely
informational and navigational; no business logic.
"""

import streamlit as st
from config.constants import APP_NAME


def render_home_page() -> None:
    """Render the Home page."""
    st.header(f"Welcome to {APP_NAME} 🧬")
    st.write(
        "Upload research papers and interact with them using AI. "
        "Ask questions, generate summaries, extract citations, identify "
        "bioinformatics entities, and compare multiple papers — all "
        "grounded in the actual text of your documents via Retrieval-"
        "Augmented Generation (RAG)."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📚 Papers Uploaded", len(st.session_state.get("uploaded_papers", [])))
    with col2:
        st.metric("💬 Chat Messages", len(st.session_state.get("chat_history", [])))
    with col3:
        st.metric("🧠 Active LLM", st.session_state.get("selected_llm_model", "—"))

    st.divider()

    st.subheader("What can you do here?")
    feature_cols = st.columns(2)
    features = [
        ("📤 Upload Papers", "Add PDF, DOCX, or TXT research papers to your library."),
        ("💬 Ask Questions", "Chat with your papers using natural language, with cited sources."),
        ("📝 Summarize", "Generate structured summaries: Abstract, Methods, Results, Conclusion."),
        ("🧬 Entity Recognition", "Extract genes, proteins, organisms, and bioinformatics tools."),
        ("🔗 Dataset Extraction", "Pull out GEO, SRA, GenBank IDs, DOIs, and PMIDs automatically."),
        ("📑 Citation Export", "Generate citations in APA, MLA, IEEE, BibTeX, and RIS formats."),
    ]
    for i, (title, desc) in enumerate(features):
        with feature_cols[i % 2]:
            st.markdown(f"**{title}**")
            st.caption(desc)

    st.divider()
    if st.button("📤 Get Started — Upload a Paper", type="primary"):
        st.session_state["active_page"] = "Upload"
        st.rerun()