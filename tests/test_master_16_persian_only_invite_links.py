import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from khatmsaz.bot import invite_links
from khatmsaz.modules.identity.models import Platform


def test_active_invite_languages_is_persian_only():
    """MASTER-16: Active invite languages are temporarily restricted to Persian."""
    assert invite_links.ACTIVE_INVITE_LANGUAGES == ("fa",)


def test_build_member_invite_links_filters_out_ar_and_en():
    """MASTER-16: build_member_invite_links must hide Arabic and English member bots by default."""
    fa_tg_bot = MagicMock(
        khatmsaz_category="QURAN",
        khatmsaz_language="fa",
        khatmsaz_username="quran_khatm_fa_bot",
        khatmsaz_platform=Platform.TELEGRAM,
    )
    fa_bale_bot = MagicMock(
        khatmsaz_category="QURAN",
        khatmsaz_language="fa",
        khatmsaz_username="quran_khatm_fa_bot",
        khatmsaz_platform=Platform.BALE,
    )
    ar_tg_bot = MagicMock(
        khatmsaz_category="QURAN",
        khatmsaz_language="ar",
        khatmsaz_username="quran_khatm_ar_bot",
        khatmsaz_platform=Platform.TELEGRAM,
    )
    en_tg_bot = MagicMock(
        khatmsaz_category="QURAN",
        khatmsaz_language="en",
        khatmsaz_username="quran_khatm_en_bot",
        khatmsaz_platform=Platform.TELEGRAM,
    )

    mock_registry = MagicMock()
    mock_registry.member_bots.return_value = [fa_tg_bot, fa_bale_bot, ar_tg_bot, en_tg_bot]

    with patch("khatmsaz.bot.invite_links.get_registry", return_value=mock_registry):
        # Default call with no langs specified (e.g. from QR button or admin approval)
        by_lang = invite_links.build_member_invite_links("QURAN", "test_tok")
        assert "fa" in by_lang
        assert "ar" not in by_lang
        assert "en" not in by_lang
        assert by_lang["fa"]["telegram"] == "https://t.me/quran_khatm_fa_bot?start=join_test_tok"
        assert by_lang["fa"]["bale"] == "https://ble.ir/quran_khatm_fa_bot?start=join_test_tok"

        # Explicitly asking for inactive langs without flag is still blocked
        by_lang_explicit = invite_links.build_member_invite_links("QURAN", "test_tok", langs=["ar", "en"])
        assert by_lang_explicit == {}

        # With include_inactive_langs=True, inactive langs are preserved for future use
        by_lang_all = invite_links.build_member_invite_links("QURAN", "test_tok", include_inactive_langs=True)
        assert "fa" in by_lang_all
        assert "ar" in by_lang_all
        assert "en" in by_lang_all


def test_format_invite_lines_single_lang_omits_redundant_header():
    """MASTER-16: Single-language invite lines should not show a redundant language label header."""
    single_lang = {
        "fa": {
            "telegram": "https://t.me/quran_khatm_fa_bot?start=join_tok1",
            "bale": "https://ble.ir/quran_khatm_fa_bot?start=join_tok1",
        }
    }
    rendered = invite_links.format_invite_lines(single_lang)
    assert "فارسی" not in rendered
    assert "عربی" not in rendered
    assert "انگلیسی" not in rendered
    assert "▫️ تلگرام: https://t.me/quran_khatm_fa_bot?start=join_tok1" in rendered
    assert "▫️ بله: https://ble.ir/quran_khatm_fa_bot?start=join_tok1" in rendered


def test_format_invite_lines_multi_lang_includes_headers():
    """MASTER-16: Multi-language invite lines include RTL-safe headers when >1 language is present."""
    multi_lang = {
        "fa": {"telegram": "https://t.me/quran_khatm_fa_bot?start=join_tok1"},
        "ar": {"telegram": "https://t.me/quran_khatm_ar_bot?start=join_tok1"},
    }
    rendered = invite_links.format_invite_lines(multi_lang)
    assert "فارسی" in rendered
    assert "عربی" in rendered
    assert "▫️ تلگرام: https://t.me/quran_khatm_fa_bot?start=join_tok1" in rendered
    assert "▫️ تلگرام: https://t.me/quran_khatm_ar_bot?start=join_tok1" in rendered
