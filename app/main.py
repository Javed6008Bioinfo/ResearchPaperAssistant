"""
Application entry point.

This file is intentionally minimal in Module 1 — it only verifies that
the environment, configuration, and logging are wired correctly.
The full Streamlit UI (sidebar, navigation, pages) is built in Module 2.

Run with: streamlit run app/main.py
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st

from config.settings import settings
from config.constants import APP_NAME, APP_VERSION
from app.utils.logger import logger, configure_logger


def bootstrap() -> None:
    """Initialize application-wide dependencies before rendering UI."""
    configure_logger()
    logger.info(f"Starting {APP_NAME} v{APP_VERSION} in '{settings.environment}' mode")


def main() -> None:
    """Application entry point."""
    bootstrap()

    st.set_page_config(
        page_title=APP_NAME,
        page_icon="🧬",
        layout="wide",
    )

    st.title(f"🧬 {APP_NAME}")
    st.caption(f"Version {APP_VERSION} — Environment: {settings.environment}")
    st.success("✅ Project scaffold is working. UI will be built in Module 2.")


if __name__ == "__main__":
    main()