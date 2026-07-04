"""
Sidebar navigation component.

Provides the primary navigation for the app (Home, Upload, Chat, Settings)
plus a compact upload summary and the Paper Information Panel. This is
the first thing rendered on every page, so it owns `active_page` state.
"""

import streamlit as st
from config.constants import APP_NAME, APP_VERSION
from app.ui.components.paper_info_panel import render_paper_info_panel

_PAGES: list[str] = ["Home", "Upload", "Chat", "Settings"]

_PAGE_ICONS: dict[str, str] = {
    "Home": "🏠",
    "Upload": "📤",
    "Chat": "💬",
    "Settings": "⚙️",
}


def render_sidebar() -> None:
    """Render the sidebar: branding, navigation, and paper info panel."""
    with st.sidebar:
        st.markdown(
            f"""
            <div class="sidebar-brand-row">
                <div class="sidebar-brand-icon">🧬</div>
                <div class="sidebar-brand">{APP_NAME}</div>
            </div>
            <div class="sidebar-subtext">v{APP_VERSION}</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-section-label">Navigation</div>', unsafe_allow_html=True)
        for page in _PAGES:
            label = f"{_PAGE_ICONS[page]}  {page}"
            is_active = st.session_state["active_page"] == page

            if st.button(label, key=f"nav_{page}", use_container_width=True,
                         type="primary" if is_active else "secondary"):
                st.session_state["active_page"] = page
                st.rerun()

        # Quick upload summary as a themed chip instead of a plain caption
        paper_count = len(st.session_state.get("uploaded_papers", []))
        st.markdown(
            f"""
            <div class="sidebar-library-chip">
                📚 <strong>{paper_count}</strong> paper(s) in library
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        render_paper_info_panel()

#         """
# Sidebar navigation component.

# Provides the primary navigation for the app (Home, Upload, Chat, Settings)
# plus a compact upload summary and the Paper Information Panel. This is
# the first thing rendered on every page, so it owns `active_page` state.
# """

# import streamlit as st
# from config.constants import APP_NAME, APP_VERSION
# from app.ui.components.paper_info_panel import render_paper_info_panel

# _PAGES: list[str] = ["Home", "Upload", "Chat", "Settings"]

# _PAGE_ICONS: dict[str, str] = {
#     "Home": "🏠",
#     "Upload": "📤",
#     "Chat": "💬",
#     "Settings": "⚙️",
# }


# def render_sidebar() -> None:
#     """Render the sidebar: branding, navigation, and paper info panel."""
#     with st.sidebar:
#         st.markdown(f'<div class="sidebar-brand">🧬 {APP_NAME}</div>', unsafe_allow_html=True)
#         st.markdown(f'<div class="sidebar-subtext">v{APP_VERSION}</div>', unsafe_allow_html=True)

#         st.divider()

#         st.markdown("**Navigation**")
#         for page in _PAGES:
#             label = f"{_PAGE_ICONS[page]}  {page}"
#             is_active = st.session_state["active_page"] == page

#             if st.button(label, key=f"nav_{page}", use_container_width=True,
#                          type="primary" if is_active else "secondary"):
#                 st.session_state["active_page"] = page
#                 st.rerun()

#         st.divider()

#         # Quick upload summary
#         paper_count = len(st.session_state.get("uploaded_papers", []))
#         st.caption(f"📚 {paper_count} paper(s) in library")

#         st.divider()

#         render_paper_info_panel()