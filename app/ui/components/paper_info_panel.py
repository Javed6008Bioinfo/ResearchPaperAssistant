"""
Paper Information Panel component.

Displays metadata about the currently active paper (filename, upload
time, page count, processing status). Rendered in the sidebar and on
the Chat page so users always know which document they're querying.

In this module, data comes from st.session_state (populated by mock
data on the Upload page). From Module 3 onward, this same component
renders real extracted metadata without any changes to this file —
that's the point of separating presentation from data population.
"""

import streamlit as st
from app.ui.components.status_badge import get_status_badge_html


def render_paper_info_panel() -> None:
    """Render the metadata card for the currently active paper."""
    active_paper = st.session_state.get("_active_paper_cache")

    st.markdown(
        '<div class="sidebar-section-label">Active Paper</div>',
        unsafe_allow_html=True,
    )

    if active_paper is None:
        st.markdown(
            """
            <div class="paper-info-empty">
                <div class="empty-icon">📄</div>
                No paper selected yet.<br>Upload one to get started.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    status = active_paper.get("status", "processing")
    badge_html = get_status_badge_html(status)

    card_html = f"""
    <div class="paper-info-card">
        <div class="paper-info-header">
            <div class="paper-info-icon">📄</div>
            <div class="paper-info-filename">{active_paper['filename']}</div>
        </div>
        <div class="paper-info-grid">
            <div>
                <div class="paper-info-label">Status</div>
                <div class="paper-info-value">{badge_html}</div>
            </div>
            <div>
                <div class="paper-info-label">Pages</div>
                <div class="paper-info-value">{active_paper.get('pages', '—')}</div>
            </div>
            <div style="grid-column: 1 / -1;">
                <div class="paper-info-label">Uploaded</div>
                <div class="paper-info-value">{active_paper['upload_time']}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# """
# Paper Information Panel component.

# Displays metadata about the currently active paper (filename, upload
# time, page count, processing status). Rendered in the sidebar and on
# the Chat page so users always know which document they're querying.

# In this module, data comes from st.session_state (populated by mock
# data on the Upload page). From Module 3 onward, this same component
# renders real extracted metadata without any changes to this file —
# that's the point of separating presentation from data population.
# """

# import streamlit as st
# from app.ui.components.status_badge import render_status_badge


# def render_paper_info_panel() -> None:
#     """Render the metadata card for the currently active paper."""
#     active_paper = st.session_state.get("_active_paper_cache")

#     st.markdown("#### 📄 Active Paper")

#     if active_paper is None:
#         st.info("No paper selected. Upload a paper to get started.")
#         return

#     with st.container():
#         st.markdown('<div class="paper-info-card">', unsafe_allow_html=True)

#         st.markdown(f"**{active_paper['filename']}**")
#         render_status_badge(active_paper["status"])

#         st.markdown("&nbsp;", unsafe_allow_html=True)  # small spacer

#         col1, col2 = st.columns(2)
#         with col1:
#             st.caption("Uploaded")
#             st.write(active_paper["upload_time"])
#         with col2:
#             st.caption("Pages")
#             st.write(active_paper.get("pages", "—"))

#         st.markdown("</div>", unsafe_allow_html=True)