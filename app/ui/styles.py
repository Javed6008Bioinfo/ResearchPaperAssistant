"""
Centralized CSS styling for the application.

Injecting custom CSS in one place (rather than scattering st.markdown
unsafe_allow_html blocks across pages) keeps the visual language
consistent and makes future theme changes a one-file edit.
"""

import streamlit as st


CUSTOM_CSS = """
<style>
    /* --- Overall app spacing --- */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* --- Sidebar branding --- */
    .sidebar-brand {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sidebar-subtext {
        font-size: 0.8rem;
        color: #8a8a8a;
        margin-bottom: 1.2rem;
    }

    /* --- Status badges --- */
    .status-badge {
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .status-processed { background-color: #d1f5d3; color: #1a7431; }
    .status-processing { background-color: #fff3cd; color: #8a6d00; }
    .status-failed { background-color: #f8d7da; color: #a41c2c; }

    /* --- Chat bubbles --- */
    .chat-bubble {
        padding: 0.9rem 1.1rem;
        border-radius: 14px;
        margin-bottom: 0.6rem;
        line-height: 1.5;
    }
    .chat-bubble-user {
        background-color: #eef2ff;
        margin-left: 15%;
    }
    .chat-bubble-assistant {
        background-color: #f6f6f6;
        margin-right: 15%;
    }
    .chat-sources {
        font-size: 0.78rem;
        color: #666666;
        margin-top: 0.4rem;
        border-top: 1px solid #e0e0e0;
        padding-top: 0.4rem;
    }

    /* --- Paper info panel --- */
    .paper-info-card {
        border: 1px solid #e6e6e6;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        background-color: #fafafa;
    }
</style>
"""


def inject_custom_css() -> None:
    """Injects the application's custom CSS once per page render."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)