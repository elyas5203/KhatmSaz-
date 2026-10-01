from uuid import uuid4

import pytest

from khatmsaz.bot.member_copy import completion_text, content_family, reminder_text, share_label
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.khatm_category.models import KhatmCategory, KhatmCategoryGroup


def _khatm(template=KhatmTemplateType.SALAWAT, **kw):
    return Khatm(
        id=uuid4(), creator_user_id=uuid4(), title="ختم آزمایشی",
        template_type=template, khatm_type=KhatmTypeEnum.COMMITMENT,
        status=KhatmStatus.ACTIVE, **kw,
    )


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
