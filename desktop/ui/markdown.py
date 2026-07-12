"""Lightweight markdown rendering for Patrick desktop chat messages."""

from __future__ import annotations

import html
import re


def render_markdown(text: str) -> str:
    """Render a small, safe subset of markdown into HTML for display."""
    escaped = html.escape(text, quote=False)

    escaped = re.sub(
        r"```(.*?)```", lambda match: _render_code_block(match.group(1)), escaped, flags=re.DOTALL
    )
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"\*(.+?)\*", r"<i>\1</i>", escaped)
    escaped = re.sub(r"`([^`]+)`", r'<code class="inline">\1</code>', escaped)
    escaped = re.sub(r"\n\n+", "<br><br>", escaped)
    escaped = re.sub(r"\n", "<br>", escaped)

    return escaped


def _render_code_block(source: str) -> str:
    code = html.escape(source.strip())
    return f'<pre class="codeblock"><code>{code}</code></pre>'
