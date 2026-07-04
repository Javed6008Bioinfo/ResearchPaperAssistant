"""
Chat bubble rendering component.

Renders a single chat message (user or assistant) with optional source
citations. Source citation rendering is a no-op placeholder here —
Module 10 (Source Citations) will populate the `sources` list with
real retrieved chunks.
"""

import streamlit as st
from typing import Any


def render_chat_bubble(role: str, content: str, sources: list[dict[str, Any]] | None = None) -> None:
    """
    Render one chat message bubble.

    Args:
        role: "user" or "assistant".
        content: The message text.
        sources: Optional list of source citation dicts, e.g.
                 [{"paper": str, "chunk_excerpt": str, "page": int}, ...].
                 Rendered only for assistant messages. Empty/None is safe.
    """
    bubble_class = "chat-bubble-user" if role == "user" else "chat-bubble-assistant"
    icon = "🧑" if role == "user" else "🤖"

    st.markdown(
        f"""
        <div class="chat-bubble {bubble_class}">
            <strong>{icon} {"You" if role == "user" else "Assistant"}</strong><br>
            {content}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if role == "assistant" and sources:
        with st.expander(f"📚 Sources ({len(sources)})"):
            for i, source in enumerate(sources, start=1):
                st.markdown(
                    f"**[{i}] {source.get('paper', 'Unknown paper')}** "
                    f"— page {source.get('page', '—')}"
                )
                st.caption(source.get("chunk_excerpt", ""))