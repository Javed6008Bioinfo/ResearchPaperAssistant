"""
Centralized CSS styling for the application.

Design system: a dark "lab notebook" theme built around a teal fluorescent-
tag accent (evoking gel stains / fluorescent protein tags used throughout
bioinformatics imaging) rather than a generic dark+violet AI-app palette.
Identifiers, filenames, page numbers, and citation excerpts are set in a
monospace utility face throughout the app, mirroring how accession numbers
and sequence data are conventionally displayed in scientific tooling.

All tokens live in :root CSS variables so future theme adjustments are a
one-file, one-variable change. Native Streamlit widgets are themed via
their stable data-testid / kind attributes rather than auto-generated
class names, which change between Streamlit versions.
"""

import streamlit as st


CUSTOM_CSS = """
<style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/0/css/font-awesome.min.css');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ============================================================
       DESIGN TOKENS
       ============================================================ */
    :root {
        --bg-ink:          #0D1117;
        --bg-surface:      #151B23;
        --bg-elevated:     #1C242E;
        --bg-elevated-hi:  #232C38;
        --border-subtle:   #262E38;
        --border-strong:   #33404D;

        --accent:          #2DD4BF;
        --accent-hover:    #5EEAD4;
        --accent-dim:      rgba(45, 212, 191, 0.14);
        --accent-dim-2:    rgba(45, 212, 191, 0.28);

        --amber:           #F2B84B;
        --amber-dim:       rgba(242, 184, 75, 0.14);
        --danger:          #F87171;
        --danger-dim:      rgba(248, 113, 113, 0.14);
        --success:         #34D399;
        --success-dim:     rgba(52, 211, 153, 0.14);

        --text-primary:    #E6EDF3;
        --text-secondary:  #9AA7B2;
        --text-muted:      #6B7680;

        --font-ui: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        --font-mono: 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace;

        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
    }

    /* ============================================================
       BASE / TYPOGRAPHY
       ============================================================ */
    html, body, [class*="css"] {
        font-family: var(--font-ui);
    }

    .stApp {
        background-color: var(--bg-ink);
        color: var(--text-primary);
    }

    h1, h2, h3, h4, h5 {
        font-family: var(--font-ui);
        font-weight: 700;
        letter-spacing: -0.01em;
        color: var(--text-primary);
    }

    p, span, label, li {
        color: var(--text-primary);
    }

    .stCaption, [data-testid="stCaptionContainer"] {
        color: var(--text-secondary) !important;
    }

    code, .stCode, [data-testid="stMarkdownContainer"] code {
        font-family: var(--font-mono) !important;
        background-color: var(--bg-elevated) !important;
        color: var(--accent) !important;
        border-radius: 4px;
    }

    hr, [data-testid="stDivider"] {
        border-color: var(--border-subtle) !important;
    }

    /* ============================================================
       LAYOUT / SPACING
       ============================================================ */
    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 4rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 1180px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
        background-color: var(--bg-surface);
    }

    /* Consistent breathing room between stacked widgets */
    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: 0.15rem;
    }

    [data-testid="stMetric"] {
        background-color: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: 1rem 1.2rem;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--accent) !important;
    }

    /* ============================================================
       SIDEBAR
       ============================================================ */
    [data-testid="stSidebar"] {
        background-color: var(--bg-surface);
        border-right: 1px solid var(--border-subtle);
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.75rem;
        padding-left: 1.25rem;
        padding-right: 1.25rem;
    }

    .sidebar-brand-row {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 0.15rem;
    }

    .sidebar-brand-icon {
        width: 34px;
        height: 34px;
        border-radius: var(--radius-sm);
        background: linear-gradient(135deg, var(--accent-dim-2), var(--accent-dim));
        border: 1px solid var(--border-strong);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.05rem;
        flex-shrink: 0;
    }

    .sidebar-brand {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.1;
    }

    .sidebar-subtext {
        font-size: 0.74rem;
        color: var(--text-muted);
        margin: 0 0 1.1rem 2.85rem;
        font-family: var(--font-mono);
        letter-spacing: 0.02em;
    }

    .sidebar-section-label {
        font-size: 0.68rem;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.09em;
        margin: 1.1rem 0 0.5rem 0.1rem;
    }

    .sidebar-library-chip {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background-color: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        padding: 0.55rem 0.8rem;
        font-size: 0.82rem;
        color: var(--text-secondary);
    }

    .sidebar-library-chip strong {
        color: var(--accent);
        font-family: var(--font-mono);
    }

    /* Sidebar nav buttons: full-width, quiet by default, accent rail when active */
    [data-testid="stSidebar"] button[kind="secondary"] {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        color: var(--text-secondary) !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-weight: 500 !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.55rem 0.8rem !important;
        box-shadow: none !important;
    }

    [data-testid="stSidebar"] button[kind="secondary"]:hover {
        background-color: var(--bg-elevated) !important;
        color: var(--text-primary) !important;
        border-color: var(--border-subtle) !important;
    }

    [data-testid="stSidebar"] button[kind="primary"] {
        background-color: var(--accent-dim) !important;
        border: 1px solid var(--accent-dim-2) !important;
        border-left: 3px solid var(--accent) !important;
        color: var(--accent) !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-weight: 600 !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.55rem 0.8rem 0.55rem calc(0.8rem - 2px) !important;
        box-shadow: none !important;
    }

    [data-testid="stSidebar"] button[kind="primary"]:hover {
        background-color: var(--accent-dim-2) !important;
        color: var(--accent-hover) !important;
    }

    /* ============================================================
       BUTTONS (main content area)
       ============================================================ */
    div[data-testid="stButton"] button,
    div[data-testid="stFormSubmitButton"] button {
        border-radius: var(--radius-sm) !important;
        font-weight: 600 !important;
        transition: background-color 0.15s ease, border-color 0.15s ease,
                    transform 0.1s ease, box-shadow 0.15s ease;
    }

    .main button[kind="primary"] {
        background-color: var(--accent) !important;
        border: 1px solid var(--accent) !important;
        color: #04211D !important;
    }

    .main button[kind="primary"]:hover {
        background-color: var(--accent-hover) !important;
        border-color: var(--accent-hover) !important;
        box-shadow: 0 0 0 3px var(--accent-dim);
        transform: translateY(-1px);
    }

    .main button[kind="secondary"] {
        background-color: var(--bg-elevated) !important;
        border: 1px solid var(--border-strong) !important;
        color: var(--text-primary) !important;
    }

    .main button[kind="secondary"]:hover {
        background-color: var(--bg-elevated-hi) !important;
        border-color: var(--accent-dim-2) !important;
        color: var(--accent) !important;
        transform: translateY(-1px);
    }

    .main button:active {
        transform: translateY(0) !important;
    }

    /* ============================================================
       FILE UPLOADER
       ============================================================ */
    [data-testid="stFileUploaderDropzone"] {
        background-color: var(--bg-surface) !important;
        border: 1.5px dashed var(--border-strong) !important;
        border-radius: var(--radius-md) !important;
    }

    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--accent-dim-2) !important;
    }

    /* ============================================================
       STATUS BADGES
       ============================================================ */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.22rem 0.65rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 600;
        font-family: var(--font-mono);
        letter-spacing: 0.01em;
        border: 1px solid transparent;
    }
    .status-processed  { background-color: var(--success-dim); color: var(--success); border-color: rgba(52,211,153,0.3); }
    .status-processing { background-color: var(--amber-dim);   color: var(--amber);   border-color: rgba(242,184,75,0.3); }
    .status-failed      { background-color: var(--danger-dim); color: var(--danger); border-color: rgba(248,113,113,0.3); }

    /* ============================================================
       PAPER INFO CARD
       ============================================================ */
    .paper-info-card {
        background: linear-gradient(160deg, var(--bg-elevated), var(--bg-surface));
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: 1rem 1.1rem;
    }

    .paper-info-header {
        display: flex;
        align-items: flex-start;
        gap: 0.65rem;
        margin-bottom: 0.7rem;
    }

    .paper-info-icon {
        width: 30px;
        height: 30px;
        flex-shrink: 0;
        border-radius: 7px;
        background-color: var(--accent-dim);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.85rem;
    }

    .paper-info-filename {
        font-size: 0.86rem;
        font-weight: 600;
        color: var(--text-primary);
        line-height: 1.3;
        word-break: break-word;
    }

    .paper-info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.6rem;
        margin-top: 0.75rem;
        padding-top: 0.7rem;
        border-top: 1px solid var(--border-subtle);
    }

    .paper-info-label {
        font-size: 0.64rem;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin-bottom: 0.15rem;
    }

    .paper-info-value {
        font-size: 0.8rem;
        color: var(--text-primary);
        font-family: var(--font-mono);
    }

    .paper-info-empty {
        border: 1px dashed var(--border-strong);
        border-radius: var(--radius-md);
        padding: 1.1rem 1rem;
        text-align: center;
        color: var(--text-muted);
        font-size: 0.82rem;
        background-color: var(--bg-surface);
    }

    .paper-info-empty .empty-icon {
        font-size: 1.3rem;
        margin-bottom: 0.35rem;
        opacity: 0.6;
    }

    /* ============================================================
       CHAT — ChatGPT-style full-width rows
       ============================================================ */
    .chat-row {
        display: flex;
        gap: 0.9rem;
        padding: 1.1rem 1.2rem;
        border-radius: var(--radius-md);
        margin-bottom: 0.6rem;
        align-items: flex-start;
    }

    .chat-row-user {
        background-color: var(--bg-surface);
        border: 1px solid var(--border-subtle);
    }

    .chat-row-assistant {
        background-color: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
        border-left: 3px solid var(--accent);
    }

    .chat-avatar {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
    }

    .chat-avatar-user {
        background-color: var(--bg-elevated-hi);
        border: 1px solid var(--border-strong);
    }

    .chat-avatar-assistant {
        background-color: var(--accent-dim);
        border: 1px solid var(--accent-dim-2);
    }

    .chat-content {
        flex: 1;
        min-width: 0;
    }

    .chat-role-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.35rem;
    }

    .chat-role-label-user { color: var(--text-secondary); }
    .chat-role-label-assistant { color: var(--accent); }

    .chat-message-text {
        font-size: 0.94rem;
        line-height: 1.65;
        color: var(--text-primary);
    }

    /* ============================================================
       SOURCES CARD
       ============================================================ */
    [data-testid="stExpander"] {
        background-color: var(--bg-surface) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
        margin-top: 0.4rem;
    }

    [data-testid="stExpander"] summary {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
    }

    .source-item {
        background-color: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        padding: 0.7rem 0.85rem;
        margin-bottom: 0.5rem;
    }

    .source-item:last-child {
        margin-bottom: 0;
    }

    .source-item-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.4rem;
    }

    .source-item-title {
        font-size: 0.78rem;
        font-weight: 600;
        color: var(--text-primary);
        font-family: var(--font-mono);
    }

    .source-item-page {
        font-size: 0.68rem;
        font-weight: 600;
        color: var(--accent);
        background-color: var(--accent-dim);
        border-radius: 999px;
        padding: 0.15rem 0.55rem;
        font-family: var(--font-mono);
        white-space: nowrap;
    }

    .source-item-excerpt {
        font-size: 0.8rem;
        color: var(--text-secondary);
        line-height: 1.55;
        border-left: 2px solid var(--border-strong);
        padding-left: 0.6rem;
        font-style: italic;
    }

    /* ============================================================
       CHAT INPUT
       ============================================================ */
    [data-testid="stChatInput"] textarea {
        background-color: var(--bg-surface) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-strong) !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: var(--text-muted) !important;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: var(--accent) !important;
    }

    /* ============================================================
       ALERTS (st.info / st.warning / st.success)
       ============================================================ */
    [data-testid="stAlertContainer"] {
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--border-subtle) !important;
    }
</style>
"""


def inject_custom_css() -> None:
    """Injects the application's custom CSS once per page render."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)