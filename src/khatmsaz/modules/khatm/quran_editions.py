"""Static Quran edition registry — total page counts per edition.

Mirrors the original project's `packages/shared/src/quran/editions.ts`.
Framework-free and dependency-free on purpose so both the allocation engine
and bot handlers can import it without pulling in anything else.
"""

QURAN_EDITIONS: dict[str, dict] = {
    "madina-hafs": {"label": "مدینه (حفص) — ۶۰۴ صفحه", "total_pages": 604},
    # Kept for backwards compatibility with already-created khatms. New
    # creation flows must use only the 604-page edition below.
    "iran-simple": {"label": "ایرانی ساده — ۵۶۰ صفحه", "total_pages": 560},
    "iran-pocket": {"label": "ایرانی جیبی — ۲۸۶ صفحه", "total_pages": 286},
}

# Product choice: the creation wizard exposes only the official 604-page
# Madina/Hafs edition. Historical records with older IDs remain readable.
QURAN_CREATION_EDITION_IDS = ("madina-hafs",)
