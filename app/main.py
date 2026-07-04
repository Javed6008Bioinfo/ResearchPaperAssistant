"""
Application entry point and page router.

Responsibilities:
    1. Bootstrap configuration and logging (Module 1).
    2. Initialize session state (single source of truth for UI data).
    3. Inject global styles.
    4. Render the sidebar (navigation + paper info).
    5. Dispatch to the currently active page.

This file intentionally contains NO business logic — it only wires
together UI components and pages.

Run with: streamlit run app/main.py
"""

import streamlit as st

from config.settings import settings
from config.constants import APP_NAME, APP_VERSION
from app.utils.logger import logger, configure_logger

from app.ui.session_state import init_session_state
from app.ui.styles import inject_custom_css
from app.ui.components.sidebar import render_sidebar

from app.ui.pages.home_page import render_home_page
from app.ui.pages.upload_page import render_upload_page
from app.ui.pages.chat_page import render_chat_page
from app.ui.pages.settings_page import render_settings_page


_PAGE_RENDERERS = {
    "Home": render_home_page,
    "Upload": render_upload_page,
    "Chat": render_chat_page,
    "Settings": render_settings_page,
}


def bootstrap() -> None:
    """Initialize application-wide dependencies before rendering UI."""
    configure_logger()
    logger.info(f"Starting {APP_NAME} v{APP_VERSION} in '{settings.environment}' mode")


def main() -> None:
    """Application entry point: bootstrap, then route to the active page."""
    bootstrap()

    st.set_page_config(
        page_title=APP_NAME,
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state()
    inject_custom_css()
    render_sidebar()

    active_page = st.session_state["active_page"]
    render_page = _PAGE_RENDERERS.get(active_page, render_home_page)
    render_page()


if __name__ == "__main__":
    main()