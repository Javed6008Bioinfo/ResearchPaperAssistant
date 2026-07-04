"""
Reusable status badge component.

Used on the Upload page (per-paper processing status) and the Paper
Information Panel. Kept separate from other components since it will
be reused as early as Module 3 when real processing statuses appear.
"""

import streamlit as st

_STATUS_LABELS: dict[str, str] = {
    "processed": "✅ Processed",
    "processing": "⏳ Processing",
    "failed": "❌ Failed",
}


def get_status_badge_html(status: str) -> str:
    """
    Returns the raw HTML string for a status badge, for embedding inline
    inside other custom HTML blocks (e.g., the Paper Information Panel's
    card) where a standalone st.markdown call would break the layout.

    Args:
        status: One of "processed", "processing", "failed".

    Returns:
        A <span> element string styled per the app's badge design tokens.
    """
    css_class = f"status-{status}" if status in _STATUS_LABELS else "status-processing"
    label = _STATUS_LABELS.get(status, f"● {status.title()}")
    return f'<span class="status-badge {css_class}">{label}</span>'


def render_status_badge(status: str) -> None:
    """
    Render a colored badge for a paper's processing status as a standalone
    Streamlit element.

    Args:
        status: One of "processed", "processing", "failed".
                Unknown statuses render as a neutral gray badge instead
                of raising an error, so malformed data never crashes the UI.
    """
    st.markdown(get_status_badge_html(status), unsafe_allow_html=True)

# """
# Reusable status badge component.

# Used on the Upload page (per-paper processing status) and the Paper
# Information Panel. Kept separate from other components since it will
# be reused as early as Module 3 when real processing statuses appear.
# """

# import streamlit as st

# _STATUS_LABELS: dict[str, str] = {
#     "processed": "✅ Processed",
#     "processing": "⏳ Processing",
#     "failed": "❌ Failed",
# }


# def render_status_badge(status: str) -> None:
#     """
#     Render a colored badge for a paper's processing status.

#     Args:
#         status: One of "processed", "processing", "failed".
#                 Unknown statuses render as a neutral gray badge instead
#                 of raising an error, so malformed data never crashes the UI.
#     """
#     css_class = f"status-{status}" if status in _STATUS_LABELS else "status-processing"
#     label = _STATUS_LABELS.get(status, f"⚪ {status.title()}")

#     st.markdown(
#         f'<span class="status-badge {css_class}">{label}</span>',
#         unsafe_allow_html=True,
#     )