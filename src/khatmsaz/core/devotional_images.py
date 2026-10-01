"""Validation and public URL resolution for small devotional images."""

from pathlib import Path
from urllib.parse import quote, urlparse


DEVOTIONAL_IMAGE_DIRNAME = "devotional-images"
_ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def validate_devotional_image_ref(value: str | None, *, local_dir: Path | None = None) -> str:
    """Accept a public HTTP(S) URL or one safe filename from the static folder."""
    ref = (value or "").strip()
    if not ref:
        return ""
    parsed = urlparse(ref)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return ref
    if parsed.scheme or parsed.netloc or Path(ref).name != ref or "/" in ref or "\\" in ref:
        raise ValueError("فقط نام فایل (بدون مسیر) یا لینک کامل http/https را وارد کنید")
    if Path(ref).suffix.lower() not in _ALLOWED_EXTENSIONS:
        raise ValueError("پسوند تصویر باید jpg، jpeg، png یا webp باشد")
    if local_dir is not None and not (local_dir / ref).is_file():
        raise ValueError(f"فایل «{ref}» در پوشهٔ تصاویر پیدا نشد")
    return ref


def resolve_devotional_image_ref(value: str | None, *, public_base_url: str) -> str | None:
    """Turn a stored filename into the public URL Telegram/Bale can fetch."""
    ref = validate_devotional_image_ref(value)
    if not ref:
        return None
    parsed = urlparse(ref)
    if parsed.scheme in {"http", "https"}:
        return ref
    base = public_base_url.strip().rstrip("/")
    if not base:
        return None
    return f"{base}/static/{DEVOTIONAL_IMAGE_DIRNAME}/{quote(ref)}"
