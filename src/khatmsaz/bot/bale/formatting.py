"""Bale Markdown formatting and HTML conversion utilities.

Bale's Bot API (tapi.bale.ai) natively renders Markdown syntax, but does NOT
support HTML tags (like <b>, <i>, <code>, <a>). Sending raw HTML tags results
in literal angle brackets and tag names appearing in chat messages.

This module converts HTML tags into Bale-compatible Markdown and unescapes
entities so text renders cleanly without breaking styling.
"""

import html
import re


def html_to_bale_markdown(text: str) -> str:
    """Converts HTML-formatted string into Bale-compatible Markdown.

    Transforms:
        <b>text</b> / <strong>text</strong> -> *text*
        <i>text</i> / <em>text</em> -> _text_
        <code>text</code> -> `text`
        <pre>text</pre> -> ```text```
        <a href="URL">TEXT</a> -> [TEXT](URL)
        <br> / <br/> -> \n
        Any other <tags> -> stripped
        HTML entities (&amp;, &lt;, &gt;, etc.) -> unescaped
    """
    if not text or not isinstance(text, str):
        return text

    s = text

    # Replace <br> and <br/> with newline
    s = re.sub(r'<br\s*/?>', '\n', s, flags=re.IGNORECASE)

    # <b> or <strong> -> *text*
    s = re.sub(r'<(?:b|strong)>(.*?)</(?:b|strong)>', r'*\1*', s, flags=re.DOTALL | re.IGNORECASE)

    # <i> or <em> -> _text_
    s = re.sub(r'<(?:i|em)>(.*?)</(?:i|em)>', r'_\1_', s, flags=re.DOTALL | re.IGNORECASE)

    # <code> -> `text`
    s = re.sub(r'<code>(.*?)</code>', r'`\1`', s, flags=re.DOTALL | re.IGNORECASE)

    # <pre> -> ```text```
    s = re.sub(r'<pre>(.*?)</pre>', r'```\1```', s, flags=re.DOTALL | re.IGNORECASE)

    # <a href="URL">TEXT</a> -> [TEXT](URL)
    s = re.sub(
        r'<a\s+(?:[^>]*?\s+)?href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
        r'[\2](\1)',
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Strip any remaining unrecognized HTML tags
    s = re.sub(r'<[^>]+>', '', s)

    # Unescape HTML entities
    s = html.unescape(s)

    return s
