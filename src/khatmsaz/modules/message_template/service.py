"""Template lookup and safe ``{{placeholder}}`` rendering."""

import re

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.message_template import repository

_PLACEHOLDER = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")
ALLOWED_PLACEHOLDERS = frozenset({"title", "start", "end", "deadline", "misses"})


def validate_body(body: str) -> None:
    """Reject malformed or unsupported placeholders before a template is stored."""
    if "{{" in body or "}}" in body:
        matches = list(_PLACEHOLDER.finditer(body))
        remainder = _PLACEHOLDER.sub("", body)
        if "{{" in remainder or "}}" in remainder:
            raise ValueError("placeholder syntax is invalid")
        unknown = sorted({match.group(1) for match in matches} - ALLOWED_PLACEHOLDERS)
        if unknown:
            raise ValueError(f"unsupported placeholders: {', '.join(unknown)}")


async def render(
    session: AsyncSession,
    key: str,
    *,
    locale: str = "fa",
    fallback_locale: str = "fa",
    **values: object,
) -> str | None:
    template = await repository.get_latest(session, key, locale)
    if template is None and locale != fallback_locale:
        template = await repository.get_latest(session, key, fallback_locale)
    if template is None:
        return None

    def replace(match: re.Match[str]) -> str:
        value = values.get(match.group(1))
        return match.group(0) if value is None else str(value)

    return _PLACEHOLDER.sub(replace, template.body)
