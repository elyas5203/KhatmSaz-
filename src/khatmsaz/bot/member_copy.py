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
    if category.group == KhatmCategoryGroup.KHUTBAH:
        return "khutbah"
    return "ziyarat" if "زیارت" in category.title else "dua"


def share_label(
    family: str, *, count: int | None = None, start: int | None = None,
    end: int | None = None, lang: str = "fa",
) -> str:
    if lang == "ar":
        if family == "quran":
            return f"الصفحات من {start} إلى {end}" if start is not None else f"{count or 1} صفحة من القرآن"
        if family == "khutbah":
            return f"القسم {start}" if start is not None else f"{count or 1} قسم من الخطبة"
        names = {"salawat": "صلوات", "dua": "الدعاء المحدد", "ziyarat": "الزيارة المحددة", "laan": "الذكر المحدد"}
        return f"{count or 1} مرة من {names.get(family, 'القراءة المحددة')}"
    if lang != "fa":
        if family == "quran":
            return f"pages {start} to {end}" if start is not None else f"{count or 1} Quran page(s)"
        if family == "khutbah":
            return f"section {start}" if start is not None else f"{count or 1} section(s) of the Khutbah"
        names = {"salawat": "Salawat", "dua": "the selected dua", "ziyarat": "the selected ziyarat", "laan": "the selected la'an"}
        return f"{count or 1} time(s) {names.get(family, 'the selected recitation')}"
    if family == "quran":
        return f"صفحات {start} تا {end}" if start is not None else f"{count or 1} صفحه از قرآن"
    if family == "khutbah":
        if start is not None and end is not None and start != end:
            return f"بخش {start} تا {end} از خطبه"
        if start is not None:
            return f"بخش {start} از خطبه"
        return f"{count or 1} بخش از خطبه"
    amount = count or 1
    labels = {
        "salawat": "صلوات",
        "dua": "دعای تعیین‌شده",
        "ziyarat": "زیارت تعیین‌شده",
        "laan": "ذکر لعن تعیین‌شده",
    }
    return f"{amount} مرتبه {labels.get(family, 'ذکر تعیین‌شده')}"


def action_verb(family: str, lang: str = "fa") -> str:
    if lang == "ar":
        return {"quran": "قراءة", "salawat": "إرسال", "dua": "قراءة", "ziyarat": "قراءة", "laan": "ذكر", "khutbah": "قراءة"}.get(family, "إتمام")
    if lang != "fa":
        return {"quran": "recite", "salawat": "send", "dua": "recite", "ziyarat": "recite", "laan": "recite", "khutbah": "recite"}.get(family, "complete")
    return {
        "quran": "قرائت",
        "salawat": "ذکر",
        "dua": "قرائت",
        "ziyarat": "قرائت",
        "laan": "قرائت",
        "khutbah": "قرائت",
    }.get(family, "انجام")


def done_button_label(family: str | None, lang: str = "fa") -> str:
    fam = family or "salawat"
    if lang == "ar":
        labels = {
            "quran": "✅ تمّت التلاوة بنجاح",
            "salawat": "✅ تم إرسال الصلوات",
            "dua": "✅ تمّت قراءة الدعاء",
            "ziyarat": "✅ تمّت الزيارة",
            "laan": "✅ تمّ الذكر بنجاح",
            "khutbah": "✅ تمّت القراءة بنجاح",
        }
        return labels.get(fam, "✅ أنجزت حصتي")
    if lang != "fa":
        labels = {
            "quran": "✅ Mark portion done",
            "salawat": "✅ Salawat sent",
            "dua": "✅ Dua recited",
            "ziyarat": "✅ Ziyarat recited",
            "laan": "✅ Recitation completed",
            "khutbah": "✅ Section completed",
        }
        return labels.get(fam, "✅ Mark share done")
    labels = {
        "quran": "✅ قرائت بخش فوق انجام شد",
        "salawat": "✅ ذکر صلوات فرستاده شد",
        "dua": "✅ قرائت دعا انجام شد",
        "ziyarat": "✅ قرائت زیارت انجام شد",
        "laan": "✅ ذکر لعن انجام شد",
        "khutbah": "✅ قرائت این بخش از خطبه انجام شد",
    }
    return labels.get(fam, "✅ قرائت بخش فوق انجام شد")


def format_deadline(deadline: int | None, user_tz: str | None = None, lang: str = "fa") -> str:
    if deadline is None:
        return "پایان امروز" if lang == "fa" else ("نهاية اليوم" if lang == "ar" else "the end of today")
    tz_label = "(به وقت ایران)" if (user_tz is None or "Tehran" in user_tz or "Iran" in user_tz) else "(به وقت محلی)"
    if 6 <= deadline < 12:
        period = "صبح امروز"
    elif 12 <= deadline < 16:
        period = "ظهر امروز"
    elif 16 <= deadline < 19:
        period = "بعدازظهر امروز"
    else:
        period = "امشب"
    return f"ساعت {deadline:02d}:00 {period} {tz_label}"


def time_greeting(hour: int | None = None, lang: str = "fa") -> str:
    if lang != "fa":
        return "Greetings 🌱"
    if hour is None:
        return "با سلام و احترام 🌱"
    if 4 <= hour < 7:
        return "با سلام و احترام، سحرگاه‌تون پربرکت 🌱"
    if 7 <= hour < 12:
        return "با سلام و احترام، صبح‌تون بخیر ☀️"
    if 12 <= hour < 16:
        return "با سلام و احترام، ظهرتون بخیر 🌞"
    if 16 <= hour < 19:
        return "با سلام و احترام، عصرتون بخیر 🌤"
    return "با سلام و احترام، شب‌تون آرام 🌙"


def reminder_text(
    khatm: Khatm, family: str, share: str, *, deadline: int | None, lang: str = "fa", audio_enabled: bool = False,
    user_tz: str | None = None, current_hour: int | None = None,
) -> str:
    if lang != "fa":
        return f"🌱 Your share in “{escape(khatm.title)}” is ready: {share}."
    deadline_text = format_deadline(deadline, user_tz=user_tz, lang=lang)
    action = action_verb(family, lang)
    btn_label = done_button_label(family, lang)
    greeting = time_greeting(current_hour, lang)
    res = (
        f"{greeting}\n\n"
        f"لطفاً {share} از ختم «{escape(khatm.title)}» را حداکثر تا {deadline_text} {action} بفرمایید "
        f"و پس از انجام، روی دکمهٔ «{btn_label}» بزنید.\n\n"
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
    if lang == "ar":
        return f"✅ تم تسجيل {share} في ختم «{escape(khatm.title)}». تقبّل الله منكم 🌱{invite_line}"
    if lang != "fa":
        return f"✅ {share} was recorded for “{escape(khatm.title)}”.{invite_line}"
    niyyat = (khatm.niyyat or "سلامتی و فرج امام عصر علیه السلام").strip()
    if niyyat.startswith("به نیت "):
        niyyat = niyyat[len("به نیت "):].strip()
    verbs = {
        "quran": "تلاوت شد",
        "salawat": "انجام شد",
        "dua": "قرائت شد",
        "ziyarat": "قرائت شد",
        "laan": "ذکر شد",
    }
    verb = verbs.get(family, "انجام شد")
    res = (
        "با سلام 🌱\n\n"
        f"✅ {share} {verb}.\n\n"
        f"اعلام شما در سیستم ثبت شد و در ثواب ختم «{escape(khatm.title)}» به نیت {escape(niyyat)} شریک شدید.\n\n"
        "خداوند از شما قبول فرماید. با تشکر."
        f"{invite_line}"
    )
    return res
