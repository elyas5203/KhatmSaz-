from uuid import uuid4

from khatmsaz.bot.handlers.start import build_join_preview_message, build_join_success_message, build_join_trust_message
from khatmsaz.modules.khatm.models import CreatorDisplayMode, Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.participation.models import Participation
from khatmsaz.modules.allocation.models import PortionUnitKind


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
    assert "این ختم از طرف خادم &lt;دل&gt; است" in text


def test_join_preview_is_informational_and_escaped():
    khatm = Khatm(
        id=uuid4(), creator_user_id=uuid4(), title="ختم <معرفی>",
        template_type=KhatmTemplateType.SALAWAT, khatm_type=KhatmTypeEnum.OPEN,
        status=KhatmStatus.ACTIVE, niyyat="نیت <خیر>", welcome_text="متن & ویژه",
    )
    text = build_join_preview_message(khatm, "سازنده <ناشناس>", 7)
    assert "عنوان: ختم &lt;معرفی&gt;" in text
    assert "سازنده &lt;ناشناس&gt; شما را به ختم «ختم &lt;معرفی&gt;» دعوت کرده است" in text
    assert "این ختم از طرف سازنده &lt;ناشناس&gt; است" in text
    assert "تعداد اعضای فعلی: 7" in text
    assert "هنوز عضو نشده‌اید" in text


def test_join_trust_message_names_creator_proxy_and_never_duplicates_niyyat_label():
    khatm = Khatm(
        id=uuid4(), creator_user_id=uuid4(), title="ختم <اعتماد>",
        template_type=KhatmTemplateType.SALAWAT, khatm_type=KhatmTypeEnum.OPEN,
        status=KhatmStatus.ACTIVE,
        niyyat="به نیت ظهور امام زمان علیه السلام — به نیابت از مادر مرحومم",
    )

    text = build_join_trust_message(khatm, "آقای <رضایی>")

    assert "آقای &lt;رضایی&gt; شما را به ختم «ختم &lt;اعتماد&gt;» دعوت کرده است" in text
    assert "این ختم از طرف آقای &lt;رضایی&gt; است" in text
    assert "به نیابت از مادر مرحومم" in text
    assert "به نیت: به نیت" not in text


def test_committed_quran_welcome_exposes_whole_portion_done_action():
    khatm = Khatm(
        id=uuid4(), creator_user_id=uuid4(), title="ختم قرآن",
        template_type=KhatmTemplateType.QURAN_PAGE,
        khatm_type=KhatmTypeEnum.COMMITMENT, status=KhatmStatus.ACTIVE,
    )
    participation = Participation(id=uuid4(), khatm_id=khatm.id, user_id=uuid4())
    stale_portion = type("Portion", (), {
        "unit_kind": PortionUnitKind.POSITIONAL, "unit_start": 1, "unit_end": 3,
    })()

    text, keyboard = build_join_success_message(
        khatm, participation, stale_portion, False, "عضو"
    )

    assert "سهم اول شما" in text
    callbacks = [button.callback_data for row in keyboard.inline_keyboard for button in row]
    assert f"done:{khatm.id}" in callbacks
    assert all(not value.startswith("contribute:") for value in callbacks)
