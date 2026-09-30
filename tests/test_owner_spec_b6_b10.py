"""Regression coverage for OWNER_SPEC_MASTER B6 through B10."""

from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock

import pytest

from khatmsaz.bot.handlers.create_khatm import _wizard_progress
from khatmsaz.bot.handlers.member_commitment import _family_prompt
from khatmsaz.bot.keyboards import creator_settings_keyboard
from khatmsaz.i18n import t
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import KhatmStatus, KhatmTemplateType, KhatmTypeEnum


def _callbacks(markup):
    return [button.callback_data for row in markup.inline_keyboard for button in row]


def test_b6_creation_explains_private_audience_and_contact_reason():
    intro = t("create_khatm.ask_template", "fa")
    contact = t("create_khatm.ask_creator_contact", "fa")
    assert "لینک اختصاصی شما" in intro
    assert "قاطی نمی‌شوند" in intro
    assert "دیگران به فهرستشان دسترسی ندارند" in intro
    assert "اگر مخاطبان ختم شما مشکلی داشتند" in contact


def test_b7_progress_summary_contains_choices_not_contact_data():
    rendered = _wizard_progress(
        {
            "template_type": "SALAWAT",
            "category_group": "DUA",
            "content_category_title": "دعای توسل",
            "khatm_type": "COMMITMENT",
            "creator_contact": "@private_contact",
        },
        "fa",
        "سؤال بعدی",
    )
    assert "انتخاب‌های شما تا اینجا" in rendered
    assert "دعای توسل" in rendered
    assert "تعهدی" in rendered
    assert "@private_contact" not in rendered


def test_b8_bot_editor_exposes_target_and_deadline():
    callbacks = _callbacks(creator_settings_keyboard(
        "kid", is_quran=False, is_commitment=True, is_open=False,
        allow_pause=True, allow_snooze=True, miss_threshold=2,
        miss_window_days=7, content_mode="AUTO", lang="fa",
    ))
    assert "cs:edit:kid:target" in callbacks
    assert "cs:edit:kid:deadline" in callbacks


@pytest.mark.asyncio
async def test_b8_runtime_editor_allows_safe_target_increase(monkeypatch):
    owner = uuid4()
    khatm = SimpleNamespace(
        id=uuid4(), creator_user_id=owner, status=KhatmStatus.ACTIVE,
        template_type=KhatmTemplateType.SALAWAT,
        khatm_type=KhatmTypeEnum.COMMITMENT, repetition_target=100,
    )
    monkeypatch.setattr(khatm_service.repository, "get_by_id", AsyncMock(return_value=khatm))
    update = AsyncMock(return_value=khatm)
    monkeypatch.setattr(khatm_service.repository, "update_creator_runtime_settings", update)

    await khatm_service.update_creator_runtime_settings(
        AsyncMock(), khatm_id=khatm.id, creator_user_id=owner,
        repetition_target=150, visibility="PRIVATE", allowed_platforms="BALE",
        reminder_tone="FORMAL", daily_deadline_hour=22,
    )
    assert update.await_args.kwargs["repetition_target"] == 150

    with pytest.raises(ValueError, match="only increase"):
        await khatm_service.update_creator_runtime_settings(
            AsyncMock(), khatm_id=khatm.id, creator_user_id=owner,
            repetition_target=99,
        )


def test_b9_each_family_has_its_own_example():
    examples = [t(f"create_khatm.welcome_example.{family}", "fa") for family in (
        "quran", "salawat", "dua", "laan",
    )]
    assert len(set(examples)) == 4
    for word, example in zip(("صفحه", "صلوات", "دعا", "لعن"), examples):
        assert word in example


def test_b10_commitment_questions_are_family_specific():
    expected = {
        "SALAWAT": "صلوات",
        "DUA": "دعا یا زیارت",
        "LAAN": "لعن",
    }
    for family, phrase in expected.items():
        count = t(_family_prompt("commit.ask_count", family), "fa")
        regular = t(
            _family_prompt("commit.ask_times_per_period", family),
            "fa", period="روز",
        )
        assert phrase in count
        assert phrase in regular
