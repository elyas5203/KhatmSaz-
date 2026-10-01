from pathlib import Path

import pytest

from khatmsaz.core.devotional_images import (
    resolve_devotional_image_ref,
    validate_devotional_image_ref,
)


def test_local_devotional_filename_is_resolved_to_public_static_url():
    assert resolve_devotional_image_ref(
        "laan-omar.jpg", public_base_url="https://panel.example.test/",
    ) == "https://panel.example.test/static/devotional-images/laan-omar.jpg"


def test_full_devotional_image_url_is_preserved():
    url = "https://cdn.example.test/images/laan.jpg"
    assert resolve_devotional_image_ref(url, public_base_url="https://panel.example.test") == url


def test_local_devotional_filename_must_exist_when_directory_is_supplied(tmp_path: Path):
    (tmp_path / "salawat.webp").write_bytes(b"image")
    assert validate_devotional_image_ref("salawat.webp", local_dir=tmp_path) == "salawat.webp"
    with pytest.raises(ValueError, match="پیدا نشد"):
        validate_devotional_image_ref("missing.webp", local_dir=tmp_path)


@pytest.mark.parametrize("value", ["../secret.jpg", "nested/image.jpg", "image.svg", "file://image.jpg"])
def test_unsafe_or_unsupported_devotional_image_ref_is_rejected(value: str):
    with pytest.raises(ValueError):
        validate_devotional_image_ref(value)
