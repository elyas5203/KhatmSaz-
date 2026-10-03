"""Warm, family-aware member reminder and completion copy."""

from html import escape

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.khatm.models import Khatm, KhatmTemplateType
from khatmsaz.modules.khatm_category import service as category_service
from khatmsaz.modules.khatm_category.models import KhatmCategoryGroup


async def content_family(session: AsyncSession, khatm: Khatm) -> str:
    if getattr(khatm, "template_type", None) == KhatmTemplateType.QURAN_PAGE:
        return "quran"
    category_id = getattr(khatm, "content_category_id", None)
    category = (
        await category_service.get(session, category_id)
        if category_id else None
    )
    if category is None:
        title = getattr(khatm, "title", "")
        if "زیارت" in title:
            return "ziyarat"
        if "دعا" in title:
            return "dua"
        if "لعن" in title:
            return "laan"
        return "salawat"
    if category.group == KhatmCategoryGroup.SALAWAT:
        return "salawat"
    if category.group == KhatmCategoryGroup.LAAN:
        return "laan"
    return "ziyarat" if "زیارت" in category.title else "dua"


def share_label(
    family: str, *, count: int | None = None, start: int | None = None,
    end: int | None = None, lang: str = "fa",
) -> str:
    if lang != "fa":
        if family == "quran":
            return f"pages {start} to {end}" if start is not None else f"{count or 1} Quran page(s)"
        names = {"salawat": "Salawat", "dua": "the selected dua", "ziyarat": "the selected ziyarat", "laan": "the selected la'an"}
        return f"{count or 1} time(s) {names.get(family, 'the selected recitation')}"
    if family == "quran":
        return f"صفحات {start} تا {end}" if start is not None else f"{count or 1} صفحه از قرآن"
    amount = count or 1
    labels = {
        "salawat": "صلوات",
        "dua": "دعای تعیین‌شده",
        "ziyarat": "زیارت تعیین‌شده",
        "laan": "ذکر لعن تعیین‌شده",
    }
    return f"{amount} مرتبه {labels.get(family, 'ذکر تعیین‌شده')}"


def reminder_text(
    khatm: Khatm, family: str, share: str, *, deadline: int | None, lang: str = "fa", audio_enabled: bool = False
) -> str:
    if lang != "fa":
        return f"🌱 Your share in “{escape(khatm.title)}” is ready: {share}."
    deadline_text = f"ساعت {deadline:02d}:00 امشب (به وقت ایران)" if deadline is not None else "پایان امروز"
    action = "قرائت" if family in {"quran", "dua", "ziyarat"} else "انجام"
    res = (
        "با سلام و احترام 🌱\n\n"
        f"لطفاً {share} از ختم «{escape(khatm.title)}» را حداکثر تا {deadline_text} {action} بفرمایید "
        "و پس از انجام، روی دکمهٔ «✅ قرائت بخش فوق انجام شد» بزنید.\n\n"
        "اگر امروز فرصت کافی ندارید، می‌توانید از یکی از دوستان یا آشنایان خود برای انجام این سهم کمک بگیرید "
        "تا برنامهٔ امروز ختم کامل بماند.\n\n"
        "در پناه حضرت صاحب‌الزمان علیه السلام"
    )
    if family == "quran" and audio_enabled:
        res += "\n\n💡 برای خاموش کردن دریافت صوت قرآن، به تنظیمات ربات بروید."
    return res


def completion_text(
    khatm: Khatm, family: str, share: str, *, invite_line: str = "", lang: str = "fa",
) -> str:
    if lang != "fa":
        return f"✅ {share} was recorded for “{escape(khatm.title)}”.{invite_line}"
    niyyat = (khatm.niyyat or "سلامتی و فرج امام عصر علیه السلام").strip()
    if niyyat.startswith("به نیت "):
        niyyat = niyyat[len("به نیت "):].strip()
    verb = "خوانده شد" if family in {"quran", "dua", "ziyarat"} else "انجام شد"
    res = (
        "با سلام 🌱\n\n"
        f"✅ {share} {verb}.\n\n"
        f"اعلام شما در سیستم ثبت شد و در ثواب ختم «{escape(khatm.title)}» به نیت {escape(niyyat)} شریک شدید.\n\n"
        "خداوند از شما قبول فرماید. با تشکر."
        f"{invite_line}"
    )
    return res
