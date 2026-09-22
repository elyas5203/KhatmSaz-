import pytest

from khatmsaz.core.db import session_scope
from khatmsaz.modules.message_template import service as template_service
from khatmsaz.modules.reminder_engine import service as reminder_service


@pytest.mark.integration
@pytest.mark.asyncio
async def test_reminder_tone_resolves_seeded_locale_template():
    async with session_scope() as session:
        class FormalKhatm:
            reminder_tone = "FORMAL"

        assert reminder_service._tone_key(FormalKhatm(), "reminder.first") == "reminder.first.formal"
        rendered = await template_service.render(
            session, "reminder.first.formal", locale="fa",
            title="ختم تست", start=10, end=11,
        )
        assert rendered is not None
        assert "یادآوری رسمی" in rendered
        assert "صفحات 10 تا 11" in rendered
