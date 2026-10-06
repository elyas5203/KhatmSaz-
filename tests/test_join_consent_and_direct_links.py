"""Owner-requested two-message join UX and direct member-bot sharing."""

from types import SimpleNamespace

import pytest

from khatmsaz.bot.handlers.member_commitment import start_commitment_mode_picker
from khatmsaz.bot.handlers.portions import _invite_friends_line, start_open_quran_setup
from khatmsaz.bot.handlers.start import build_join_consent_message
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.khatm.models import KhatmTemplateType, KhatmTypeEnum


class State:
    def __init__(self):
        self.data = {}
        self.state = None

    async def get_data(self):
        return self.data

    async def update_data(self, **values):
        self.data.update(values)

    async def set_state(self, value):
        self.state = value


class Message:
    message_id = 10

    def __init__(self):
        self.answers = []

    async def answer(self, text, **kwargs):
        sent = SimpleNamespace(message_id=20 + len(self.answers))
        self.answers.append((text, kwargs, sent))
        return sent


def _khatm(mode):
    return SimpleNamespace(
        title="ختم آزمایشی", template_type=KhatmTemplateType.SALAWAT,
        khatm_type=mode, repetition_target=100, content_category_id=None,
        niyyat="سلامتی", welcome_text="خوش آمدید",
    )


def test_consent_copy_is_custom_for_commitment_and_open_khatms():
    committed = build_join_consent_message(_khatm(KhatmTypeEnum.COMMITMENT), "سازنده", 2)
    open_join = build_join_consent_message(_khatm(KhatmTypeEnum.OPEN), "سازنده", 2)

    assert "این ختم تعهدی است" in committed
    assert "تعهد شرعی" in committed
    assert "دِین" in committed
    assert "این ختم آزاد است" in open_join
    assert "تعهد شرعی یا دِینی" in open_join
    assert "احترام به جمع" in open_join


def test_fixed_daily_commitment_consent_units_by_family():
    # 1. La'an commitment
    laan_khatm = _khatm(KhatmTypeEnum.COMMITMENT)
    laan_khatm.commitment_policy = "FIXED_DAILY"
    laan_khatm.daily_commitment_amount = 3
    laan_khatm.template_type = KhatmTemplateType.SALAWAT
    laan_text = build_join_consent_message(
        laan_khatm, "سازنده", 5, lang="fa", category_group="LAAN", category_title="لعن زیارت عاشورا"
    )
    assert "مقدار 3 مرتبه" in laan_text
    assert "صلوات" not in laan_text

    # 2. Salawat commitment
    salawat_khatm = _khatm(KhatmTypeEnum.COMMITMENT)
    salawat_khatm.commitment_policy = "FIXED_DAILY"
    salawat_khatm.daily_commitment_amount = 100
    salawat_khatm.template_type = KhatmTemplateType.SALAWAT
    salawat_text = build_join_consent_message(
        salawat_khatm, "سازنده", 5, lang="fa", category_group="SALAWAT"
    )
    assert "مقدار 100 صلوات" in salawat_text

    # 3. Quran commitment
    quran_khatm = _khatm(KhatmTypeEnum.COMMITMENT)
    quran_khatm.commitment_policy = "FIXED_DAILY"
    quran_khatm.daily_commitment_amount = 2
    quran_khatm.template_type = KhatmTemplateType.QURAN_PAGE
    quran_text = build_join_consent_message(
        quran_khatm, "سازنده", 5, lang="fa"
    )
    assert "مقدار 2 صفحه" in quran_text


def test_commitment_without_target_never_looks_open_and_preview_heading_is_hidden():
    khatm = _khatm(KhatmTypeEnum.COMMITMENT)
    khatm.repetition_target = None
    text = build_join_consent_message(khatm, "سازنده", 0)
    assert "پیش‌نمایش ختم" not in text
    assert "حالت: تعهدی" in text
    assert "حالت: آزاد" not in text


@pytest.mark.asyncio
async def test_repetition_questions_are_a_separate_updating_message():
    message, state = Message(), State()
    await start_commitment_mode_picker(
        message, state, "participant-id", "fa",
        summary="این کارت خوش‌آمد باید ثابت بماند", family="SALAWAT",
    )

    assert len(message.answers) == 1
    assert "این کارت خوش‌آمد باید ثابت بماند" not in message.answers[0][0]
    assert state.data["_cwiz_mid"] == message.answers[0][2].message_id
    assert state.data["commit_summary"] == ""


@pytest.mark.asyncio
async def test_open_quran_questions_are_separate_from_welcome():
    message, state = Message(), State()
    await start_open_quran_setup(
        message, state, khatm_id="khatm-id", lang="fa",
        summary="کارت خوش‌آمد ثابت",
    )

    assert len(message.answers) == 1
    assert "کارت خوش‌آمد ثابت" not in message.answers[0][0]
    assert state.data["_join_wizard_mid"] == message.answers[0][2].message_id
    assert state.data["_join_summary"] == ""


@pytest.mark.asyncio
async def test_completion_share_link_goes_directly_to_current_member_bot(monkeypatch):
    async def create_invitation(*args, **kwargs):
        return "direct-token"

    monkeypatch.setattr(
        "khatmsaz.bot.handlers.portions.invitation_service.create_invitation",
        create_invitation,
    )
    bot = SimpleNamespace(khatmsaz_username="Khatm_Saz_bot")
    line = await _invite_friends_line(
        object(), SimpleNamespace(id="khatm-id"), "creator-id",
        Platform.TELEGRAM, "fa", bot=bot,
    )

    assert "https://t.me/Khatm_Saz_bot?start=join_direct-token" in line
    assert "/join/direct-token" not in line
