"""Startup seed for admin-curated devotional TEXT (dua / ziyarat).

Owner workflow: the owner hands us the full text of a dua/ziyarat, we store
it here, and a plain `git pull && systemctl restart khatmsaz` makes it live —
no manual DB step and no `/manage_content` upload needed. Images/audio are
still added later via the admin channel/panel (they live in separate columns
and the `devotional_media` table, so this text seed never touches them).

Each entry's text is auto-split into <=~3500-char chunks joined by the record
separator ``\x1e`` — the exact delimiter `portions._send_recitation_content`
splits on before sending each piece as its own Telegram/Bale message (a single
message caps at 4096 chars, and Ziyarat Ashura is far longer).

To connect a text to a khatm, link a `KhatmCategory.devotional_slug` to the
slug below (or, for Ziyarat Ashura, a category whose title contains «عاشورا»
matches the built-in hint automatically).

Seeding is an idempotent upsert keyed on slug (see
`content.service.register_devotional_text`): editing a text here and
restarting re-applies it.
"""
from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from . import service as content_service
from ._devotional_texts import AHD, ALE_YASIN, FARAJ, ZIYARAT_ASHURA

logger = logging.getLogger(__name__)

# Telegram/Bale hard cap is 4096 chars per message; stay well under it so a
# couplet is never split mid-line.
_CHUNK_LIMIT = 3500
_RECORD_SEPARATOR = "\x1e"


def _chunk(text: str, limit: int = _CHUNK_LIMIT) -> str:
    """Greedily pack blank-line-separated paragraphs into <=limit chunks,
    joined by the record separator the delivery code splits on."""
    paragraphs = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) > limit and current:
            chunks.append(current)
            current = para
        else:
            current = candidate
    if current:
        chunks.append(current)
    return _RECORD_SEPARATOR.join(chunks)


# (slug, content_type, title, raw_text)
_DEVOTIONAL_TEXTS: list[tuple[str, str, str, str]] = [
    ("ziyarat-ashura", "ZIYARAT", "زیارت عاشورا", ZIYARAT_ASHURA),
    ("dua-ale-yasin", "DUA", "دعای آل یاسین", ALE_YASIN),
    ("dua-faraj", "DUA", "دعای فرج", FARAJ),
    ("dua-ahd", "DUA", "دعای عهد", AHD),
]


async def seed_devotional_texts(session: AsyncSession) -> dict[str, object]:
    """Idempotently upsert every curated devotional text. Safe to run on
    every startup — returns a small summary for logging."""
    seeded: list[str] = []
    for slug, content_type, title, raw_text in _DEVOTIONAL_TEXTS:
        text_body = _chunk(raw_text)
        await content_service.register_devotional_text(
            session,
            content_type=content_type,
            slug=slug,
            title=title,
            text_body=text_body,
        )
        seeded.append(slug)
    return {"seeded": seeded, "count": len(seeded)}
