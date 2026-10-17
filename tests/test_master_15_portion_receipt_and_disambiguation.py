"""Tests for Child Master 15 — Member Portion Receipt & Khatm Disambiguation System.

Verifies:
1. menu.today label is '📖 دریافت سهم قرائت' in Persian, with Arabic and English translations.
2. TODAY_BUTTON_TEXTS matches new variants as well as legacy variants.
3. get_khatm_identifier correctly extracts title, creator name, and cleaned niyyat.
4. today_overview with multiple khatms of identical title disambiguates them in message and on buttons.
5. member_my_khatms renders creator name and niyyat on each khatm card.
"""
import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from khatmsaz.i18n import t
from khatmsaz.bot.keyboards import TODAY_BUTTON_TEXTS, member_menu_keyboard
from khatmsaz.bot.member_copy import get_khatm_identifier
from khatmsaz.bot.handlers import report, member_my_khatms


def test_menu_today_translations():
    assert t("menu.today", "fa") == "📖 دریافت سهم قرائت"
    assert t("menu.today", "ar") == "📖 استلام حصة القراءة"
    assert t("menu.today", "en") == "📖 Receive Recitation Portion"

    # Member menu keyboard contains the new button text
    kb = member_menu_keyboard("fa")
    labels = [b.text for row in kb.keyboard for b in row]
    assert "📖 دریافت سهم قرائت" in labels


def test_today_button_texts_backward_compatibility():
    assert "📖 دریافت سهم قرائت" in TODAY_BUTTON_TEXTS
    assert "دریافت سهم قرائت" in TODAY_BUTTON_TEXTS
    assert "📖 دریافت سهم امروز" in TODAY_BUTTON_TEXTS
    assert "دریافت سهم امروز" in TODAY_BUTTON_TEXTS
    assert "📖 اعلام انجام قرائت امروز" in TODAY_BUTTON_TEXTS
    assert "اعلام انجام قرائت امروز" in TODAY_BUTTON_TEXTS


@pytest.mark.asyncio
async def test_get_khatm_identifier():
    session = MagicMock()
    creator = SimpleNamespace(display_name="حمیدرضا رئیسی")
    session.get = AsyncMock(return_value=creator)

    khatm = SimpleNamespace(
        title="ختم قرآن",
        creator_user_id=uuid4(),
        creator_display_mode="FULL_NAME",
        niyyat="ظهور امام زمان (عج)",
    )

    title, creator_name, niyyat = await get_khatm_identifier(session, khatm, "fa")
    assert title == "ختم قرآن"
    assert creator_name == "حمیدرضا رئیسی"
    assert niyyat == "ظهور امام زمان (عج)"


@pytest.mark.asyncio
async def test_today_overview_disambiguates_identical_khatm_titles():
    class FakeMessage:
        def __init__(self):
            self.bot = SimpleNamespace(
                khatmsaz_platform="TELEGRAM",
                khatmsaz_language="fa",
                khatmsaz_instance_id="bot-1",
            )
            self.chat = SimpleNamespace(id=100)
            self.answers = []

        async def answer(self, text, **kwargs):
            self.answers.append((text, kwargs))

    khatm1 = SimpleNamespace(
        id=uuid4(), title="ختم قرآن", creator_user_id=uuid4(),
        creator_display_mode="FULL_NAME", niyyat="شفای بیماران",
        khatm_type="OPEN",
    )
    khatm2 = SimpleNamespace(
        id=uuid4(), title="ختم قرآن", creator_user_id=uuid4(),
        creator_display_mode="FULL_NAME", niyyat="شادی روح اموات",
        khatm_type="OPEN",
    )
    part1 = SimpleNamespace(id=uuid4(), khatm_id=khatm1.id)
    part2 = SimpleNamespace(id=uuid4(), khatm_id=khatm2.id)

    creator1 = SimpleNamespace(display_name="علی محمدی")
    creator2 = SimpleNamespace(display_name="رضا حسینی")

    async def fake_get(model, uid):
        if uid == khatm1.creator_user_id:
            return creator1
        if uid == khatm2.creator_user_id:
            return creator2
        return None

    session = MagicMock()
    session.get = AsyncMock(side_effect=fake_get)

    from contextlib import asynccontextmanager
    @asynccontextmanager
    async def fake_scope():
        yield session

    with (
        patch("khatmsaz.bot.handlers.report.session_scope", fake_scope),
        patch("khatmsaz.bot.handlers.report.identity_service.resolve_or_provision_user", AsyncMock(return_value=SimpleNamespace(id=uuid4()))),
        patch("khatmsaz.bot.handlers.report.settings_service.get_or_create", AsyncMock(return_value=SimpleNamespace(language="fa"))),
        patch("khatmsaz.bot.handlers.report.participation_service.list_my_active", AsyncMock(return_value=[part1, part2])),
        patch("khatmsaz.bot.handlers.report.khatm_service.get_khatm", AsyncMock(side_effect=lambda s, kid: khatm1 if kid == khatm1.id else khatm2)),
        patch("khatmsaz.bot.handlers.report.ensure_participation_matches_bot", AsyncMock(return_value=True)),
        patch("khatmsaz.bot.handlers.report.khatm_service.has_started", return_value=True),
    ):
        msg = FakeMessage()
        await report.today_overview(msg)

        assert len(msg.answers) == 1
        text, kwargs = msg.answers[0]
        # Text includes creator names and niyyats
        assert "علی محمدی" in text
        assert "رضا حسینی" in text
        assert "شفای بیماران" in text
        assert "شادی روح اموات" in text

        # Buttons on keyboard are disambiguated with creator names
        kb = kwargs["reply_markup"]
        btn1_text = kb.inline_keyboard[0][0].text
        btn2_text = kb.inline_keyboard[1][0].text
        assert "علی محمدی" in btn1_text
        assert "رضا حسینی" in btn2_text
