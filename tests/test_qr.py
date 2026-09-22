import pytest

from khatmsaz.bot.qr import build_qr_png


def test_build_qr_png_is_nonempty_png():
    data = build_qr_png("https://t.me/Khatm_Saz_bot?start=join_test")
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(data) > 500


def test_build_qr_png_rejects_non_web_values():
    with pytest.raises(ValueError):
        build_qr_png("/start join_test")
