"""
Chat message rendering component.

Renders a single chat turn (user or assistant) as a full-width row with
an avatar chip, following the alternating-row pattern used by ChatGPT
rather than floating, margin-offset bubbles. Optional source citations
render as individual cards below assistant messages.

Source citation rendering is currently based on placeholder data —
Module 10 (Source Citations) will populate the `sources` list with real
retrieved chunks; this file's rendering logic does not need to change
when that happens.
"""

import html
import streamlit as st
from typing import Any


def render_chat_bubble(role: str, content: str, sources: list[dict[str, Any]] | None = None) -> None:
    """
    Render one chat message as a full-width row.

    Args:
        role: "user" or "assistant".
        content: The message text.
        sources: Optional list of source citation dicts, e.g.
                 [{"paper": str, "chunk_excerpt": str, "page": int}, ...].
                 Rendered only for assistant messages. Empty/None is safe.
    """
    is_user = role == "user"
    row_class = "chat-row-user" if is_user else "chat-row-assistant"
    avatar_class = "chat-avatar-user" if is_user else "chat-avatar-assistant"
    label_class = "chat-role-label-user" if is_user else "chat-role-label-assistant"
    icon = "🧑" if is_user else "🧬"
    role_label = "You" if is_user else "Assistant"

    # Escape user-provided content to prevent raw HTML/markdown injection
    # from breaking the layout, while still allowing basic readability
    # (line breaks) in longer answers.
    safe_content = html.escape(content).replace("\n", "<br>")

    st.markdown(
        f"""
        <div class="chat-row {row_class}">
            <div class="chat-avatar {avatar_class}">{icon}</div>
            <div class="chat-content">
                <div class="chat-role-label {label_class}">{role_label}</div>
                <div class="chat-message-text">{safe_content}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if role == "assistant" and sources:
        with st.expander(f"📚 Sources ({len(sources)})"):
            for i, source in enumerate(sources, start=1):
                paper_name = html.escape(str(source.get("paper", "Unknown paper")))
                page = html.escape(str(source.get("page", "—")))
                excerpt = html.escape(source.get("chunk_excerpt", ""))

                st.markdown(
                    f"""
                    <div class="source-item">
                        <div class="source-item-header">
                            <span class="source-item-title">[{i}] {paper_name}</span>
                            <span class="source-item-page">p. {page}</span>
                        </div>
                        <div class="source-item-excerpt">{excerpt}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# """
# Chat bubble rendering component.

# Renders a single chat message (user or assistant) with optional source
# citations. Source citation rendering is a no-op placeholder here —
# Module 10 (Source Citations) will populate the `sources` list with
# real retrieved chunks.
# """

# import streamlit as st
# from typing import Any


# def render_chat_bubble(role: str, content: str, sources: list[dict[str, Any]] | None = None) -> None:
#     """
#     Render one chat message bubble.

#     Args:
#         role: "user" or "assistant".
#         content: The message text.
#         sources: Optional list of source citation dicts, e.g.
#                  [{"paper": str, "chunk_excerpt": str, "page": int}, ...].
#                  Rendered only for assistant messages. Empty/None is safe.
#     """
#     bubble_class = "chat-bubble-user" if role == "user" else "chat-bubble-assistant"
#     icon = "🧑" if role == "user" else "🤖"

#     st.markdown(
#         f"""
#         <div class="chat-bubble {bubble_class}">
#             <strong>{icon} {"You" if role == "user" else "Assistant"}</strong><br>
#             {content}
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )

#     if role == "assistant" and sources:
#         with st.expander(f"📚 Sources ({len(sources)})"):
#             for i, source in enumerate(sources, start=1):
#                 st.markdown(
#                     f"**[{i}] {source.get('paper', 'Unknown paper')}** "
#                     f"— page {source.get('page', '—')}"
#                 )
#                 st.caption(source.get("chunk_excerpt", ""))