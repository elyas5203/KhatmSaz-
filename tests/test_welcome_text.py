from uuid import uuid4

from khatmsaz.bot.handlers.start import build_join_preview_message, build_join_success_message
from khatmsaz.modules.khatm.models import CreatorDisplayMode, Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.participation.models import Participation


def test_creator_welcome_is_included_and_html_escaped():
    khatm = Khatm(
        id=uuid4(), creator_user_id=uuid4(), title="عنوان <تست>",
        template_type=KhatmTemplateType.SALAWAT, khatm_type=KhatmTypeEnum.OPEN,
        status=KhatmStatus.ACTIVE, welcome_text="خوش آمدید <دوست> & همراه",
    )
    participation = Participation(id=uuid4(), khatm_id=khatm.id, user_id=uuid4())
    text, _ = build_join_success_message(khatm, participation, None, False, "نام <کاربر>")
    assert "&lt;دوست&gt; &amp; همراه" in text
    assert "&lt;کاربر&gt;" in text
    assert "عنوان &lt;تست&gt;" in text


def test_creator_display_name_is_included_and_escaped():
    khatm = Khatm(
        id=uuid4(), creator_user_id=uuid4(), title="ختم تست",
        template_type=KhatmTemplateType.SALAWAT, khatm_type=KhatmTypeEnum.OPEN,
        status=KhatmStatus.ACTIVE, creator_display_mode=CreatorDisplayMode.PSEUDONYM.value,
        creator_pseudonym="خادم <دل>",
    )
    participation = Participation(id=uuid4(), khatm_id=khatm.id, user_id=uuid4())
    text, _ = build_join_success_message(
        khatm, participation, None, False, "عضو", "خادم <دل>"
    )
    assert "سازنده: خادم &lt;دل&gt;" in text


def test_join_preview_is_informational_and_escaped():
    khatm = Khatm(
        id=uuid4(), creator_user_id=uuid4(), title="ختم <معرفی>",
        template_type=KhatmTemplateType.SALAWAT, khatm_type=KhatmTypeEnum.OPEN,
        status=KhatmStatus.ACTIVE, niyyat="نیت <خیر>", welcome_text="متن & ویژه",
    )
    text = build_join_preview_message(khatm, "سازنده <ناشناس>", 7)
    assert "عنوان: ختم &lt;معرفی&gt;" in text
    assert "سازنده: سازنده &lt;ناشناس&gt;" in text
    assert "تعداد اعضای فعلی: 7" in text
    assert "هنوز عضو نشده‌اید" in text
