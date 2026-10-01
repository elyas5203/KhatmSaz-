from pathlib import Path

from khatmsaz.i18n import t


def test_private_join_callbacks_are_registered_on_both_dispatchers():
    source = Path("src/khatmsaz/bootstrap.py").read_text(encoding="utf-8")
    shared = source.split("_shared_module_paths = [", 1)[1].split("]", 1)[0]
    assert '"khatmsaz.bot.handlers.join_requests"' in shared
    assert "dp_member.include_router(join_requests_router)" not in source


def test_salawat_tone_examples_name_salawat_instead_of_quran_reading():
    text = t("create_khatm.ask_reminder_tone", "fa", share="صلوات‌های امروز")
    assert "صلوات‌های امروز" in text
    assert "سهم امروز شما آمادهٔ قرائت" not in text


def test_private_join_notice_contains_recognition_fields():
    text = t(
        "join.private_request_creator_notice", "fa",
        title="ختم پدر", name="علی رضایی", phone="+989121234567",
        identities="TELEGRAM: 123456",
    )
    assert "علی رضایی" in text
    assert "+989121234567" in text
    assert "TELEGRAM: 123456" in text
