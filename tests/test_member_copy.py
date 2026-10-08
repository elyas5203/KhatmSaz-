from uuid import uuid4

import pytest

from khatmsaz.bot.member_copy import completion_text, content_family, reminder_text, share_label
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.khatm_category.models import KhatmCategory, KhatmCategoryGroup


def _khatm(template=KhatmTemplateType.SALAWAT, **kw):
    params = {
        "id": uuid4(),
        "creator_user_id": uuid4(),
        "title": "ختم آزمایشی",
        "template_type": template,
        "khatm_type": KhatmTypeEnum.COMMITMENT,
        "status": KhatmStatus.ACTIVE,
    }
    params.update(kw)
    return Khatm(**params)


def test_formal_quran_reminder_mentions_deadline_action_and_help():
    khatm = _khatm(KhatmTemplateType.QURAN_PAGE, daily_deadline_hour=23)
    text = reminder_text(khatm, "quran", share_label("quran", start=56, end=57), deadline=23)
    assert "صفحات 56 تا 57" in text
    assert "ساعت 23:00 امشب (به وقت ایران)" in text
    assert "قرائت بخش فوق انجام شد" in text
    assert "دوستان یا آشنایان" in text
    assert "صاحب‌الزمان علیه السلام" in text


def test_completion_mentions_same_khatm_intention_and_direct_invite():
    khatm = _khatm(niyyat="به نیت سلامتی مادرم")
    text = completion_text(
        khatm, "salawat", share_label("salawat", count=100),
        invite_line="\n\nدعوت:\nhttps://t.me/member_bot?start=join_token",
    )
    assert "100 مرتبه صلوات انجام شد" in text
    assert "ختم «ختم آزمایشی»" in text
    assert "به نیت سلامتی مادرم" in text
    assert "به نیت به نیت" not in text
    assert "https://t.me/member_bot?start=join_token" in text


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("group", "title", "expected"),
    [
        (KhatmCategoryGroup.SALAWAT, "صلوات", "salawat"),
        (KhatmCategoryGroup.LAAN, "لعن عمر", "laan"),
        (KhatmCategoryGroup.DUA, "دعای عهد", "dua"),
        (KhatmCategoryGroup.DUA, "زیارت عاشورا", "ziyarat"),
    ],
)
async def test_content_family_distinguishes_member_sections(monkeypatch, group, title, expected):
    category_id = uuid4()
    category = KhatmCategory(id=category_id, group=group, title=title, sort_order=0)

    async def fake_get(_session, _category_id):
        return category

    monkeypatch.setattr("khatmsaz.bot.member_copy.category_service.get", fake_get)
    assert await content_family(object(), _khatm(content_category_id=category_id)) == expected


def test_time_aware_greeting_and_deadline_formatting():
    from khatmsaz.bot.member_copy import time_greeting, format_deadline, done_button_label

    # Greeting by hour
    assert "صبح‌تون بخیر" in time_greeting(9)
    assert "ظهرتون بخیر" in time_greeting(13)
    assert "عصرتون بخیر" in time_greeting(17)
    assert "شب‌تون آرام" in time_greeting(21)
    assert "سحرگاه‌تون پربرکت" in time_greeting(5)

    # Deadline by hour
    assert "صبح امروز" in format_deadline(9)
    assert "ظهر امروز" in format_deadline(13)
    assert "بعدازظهر امروز" in format_deadline(17)
    assert "امشب" in format_deadline(22)

    # Button labels by family
    assert "قرائت بخش فوق انجام شد" in done_button_label("quran")
    assert "ذکر صلوات فرستاده شد" in done_button_label("salawat")
    assert "قرائت دعا" in done_button_label("dua")
    assert "قرائت زیارت" in done_button_label("ziyarat")
    assert "ذکر لعن انجام شد" in done_button_label("laan")


def test_reminder_text_for_morning_salawat():
    khatm = _khatm(KhatmTemplateType.SALAWAT)
    text = reminder_text(
        khatm, "salawat", "100 صلوات", deadline=10, current_hour=9
    )
    assert "صبح‌تون بخیر" in text
    assert "10:00 صبح امروز" in text
    assert "ذکر صلوات فرستاده شد" in text
    assert "امشب" not in text


def test_completion_message_customization_creator_vs_member_and_niyyat():
    from khatmsaz.modules.completion.service import _message

    class DummyStats:
        total_members = 15
        total_portions = 30
        completed_portions = 30
        contribution_total = 1000

    quran_khatm = _khatm(KhatmTemplateType.QURAN_PAGE, title="ختم قرآن نور", niyyat="به نیت فرج آقا امام زمان")
    salawat_khatm = _khatm(KhatmTemplateType.SALAWAT, title="ختم صلوات نور", niyyat="شفای بیماران")

    # Creator message
    creator_msg = _message(quran_khatm.title, DummyStats(), "fa", khatm=quran_khatm, is_creator=True)
    assert "تبریک و خداقوت به بانی محترم" in creator_msg
    assert "🤲 به نیت: فرج آقا امام زمان" in creator_msg
    assert "📖 سهم‌های تکمیل‌شده: 30 / 30" in creator_msg
    assert "👥 تعداد همراهان: 15" in creator_msg

    # Member message
    member_msg = _message(salawat_khatm.title, DummyStats(), "fa", khatm=salawat_khatm, is_creator=False)
    assert "با همراهی شما به پایان رسید" in member_msg
    assert "خدا از همه قبول کند" in member_msg
    assert "🤲 به نیت: شفای بیماران" in member_msg
    assert "📿 سهم‌های تکمیل‌شده: 30 / 30" in member_msg
    assert "تبریک و خداقوت به بانی محترم" not in member_msg


def test_monthly_report_render_taxonomy_support():
    from khatmsaz.modules.monthly_report.service import _render
    from khatmsaz.modules.reporting.service import ClosedMonthReport

    report = ClosedMonthReport(
        quran_pages=15,
        salawat_count=500,
        completed_khatms=2,
        dua_count=10,
        laan_count=50,
    )
    rendered_fa = _render("2026-09", report, "fa")
    assert "گزارش مثبت شما برای ماه 2026-09" in rendered_fa
    assert "📖 صفحه قرآن: 15" in rendered_fa
    assert "📿 صلوات: 500" in rendered_fa
    assert "🤲 ادعیه و زیارات: 10" in rendered_fa
    assert "⚡ اذکار و برائت: 50" in rendered_fa
    assert "🎉 ختم به‌پایان‌رسیده: 2" in rendered_fa


