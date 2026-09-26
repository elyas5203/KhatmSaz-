from types import SimpleNamespace

import pytest

from khatmsaz.modules.reminder_engine import service
from khatmsaz.modules.notification.models import NotificationKind


@pytest.mark.asyncio
async def test_daily_digest_combines_multiple_khatms_for_one_user(monkeypatch):
    sent = []
    logged = []
    user_id = "user"
    p1 = SimpleNamespace(id="p1", user_id=user_id, joined_via_bot_instance_id=None)
    p2 = SimpleNamespace(id="p2", user_id=user_id, joined_via_bot_instance_id=None)
    k1 = SimpleNamespace(title="قرآن صبح")
    k2 = SimpleNamespace(title="قرآن شب")
    portion1 = SimpleNamespace(unit_start=1, unit_end=2)
    portion2 = SimpleNamespace(unit_start=3, unit_end=4)

    async def fake_render(session, key, *, locale="fa", **values):
        return f"{values['title']}: {values['start']}-{values['end']}"

    async def fake_identities(session, target_user_id):
        return [SimpleNamespace(platform=SimpleNamespace(value="TELEGRAM"), subject="123")]

    async def fake_notify(platform, subject, text, *, bot_instance_id=None):
        sent.append((platform, subject, text))

    async def fake_record(session, participation_id, kind):
        logged.append((participation_id, kind))

    monkeypatch.setattr(service.template_service, "render", fake_render)
    monkeypatch.setattr(service.identity_service, "list_identities_for_user", fake_identities)
    monkeypatch.setattr(service.notification_service, "record_sent", fake_record)

    await service._send_daily_digest(
        object(), fake_notify,
        [(p1, k1, portion1, "en", True), (p2, k2, portion2, "en", True)],
    )

    assert len(sent) == 1
    assert "قرآن صبح" in sent[0][2]
    assert "قرآن شب" in sent[0][2]
    assert logged == [("p1", NotificationKind.DAILY_REMINDER), ("p2", NotificationKind.DAILY_REMINDER)]
