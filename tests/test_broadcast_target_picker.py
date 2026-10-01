"""Regression for per-khatm broadcast targeting (owner request 2026-09-27):
tapping «📢 ارسال پیام گروهی» must first show a khatm picker («به همهٔ ختم‌ها»
+ one row per active khatm), not blast the whole audience immediately."""
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Chat, Message, Update, User

from khatmsaz.bot.handlers import creator_broadcast as cb
from khatmsaz.modules.identity.models import UserRole
from khatmsaz.modules.khatm.models import KhatmStatus


def _text_update(update_id: int, text: str, chat_id: int = 9303) -> Update:
    return Update(
        update_id=update_id,
        message=Message(
            message_id=update_id,
            date=datetime.now(timezone.utc),
            chat=Chat(id=chat_id, type="private"),
            from_user=User(id=chat_id, is_bot=False, first_name="Creator"),
            text=text,
        ),
    )


@pytest.mark.asyncio
async def test_broadcast_shows_khatm_picker(monkeypatch):
    creator = SimpleNamespace(id=uuid4(), role=UserRole.CREATOR)
    khatms = [
        SimpleNamespace(id=uuid4(), title="ختم قرآن", status=KhatmStatus.ACTIVE),
        SimpleNamespace(id=uuid4(), title="ختم صلوات", status=KhatmStatus.ACTIVE),
        SimpleNamespace(id=uuid4(), title="ختم لغو شده", status=KhatmStatus.CANCELLED),
    ]
    sent = []

    class _Scope:
        async def __aenter__(self): return object()
        async def __aexit__(self, *a): return False

    monkeypatch.setattr(cb, "session_scope", lambda: _Scope())

    async def fake_user(*a, **k): return creator
    async def fake_list(*a, **k): return khatms
    monkeypatch.setattr(cb.identity_service, "resolve_or_provision_user", fake_user)
    monkeypatch.setattr(cb.khatm_service, "list_my_created", fake_list)

    async def capture(self, text, **kwargs):
        sent.append((text, kwargs.get("reply_markup")))
        return self
    monkeypatch.setattr(Message, "answer", capture)

    bot = Bot("123456:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi")
    bot._me = User(id=123456, is_bot=True, first_name="KhatmSaz", username="khatmsaz_test_bot")
    dp = Dispatcher(storage=MemoryStorage())
    cb.router._parent_router = None
    dp.include_router(cb.router)
    try:
        await dp.feed_update(bot, _text_update(1, "📢 ارسال پیام گروهی"))
    finally:
        await bot.session.close()

    assert sent, "broadcast entry produced no message"
    text, markup = sent[-1]
    assert markup is not None, "no khatm picker keyboard shown"
    labels = [btn.text for row in markup.inline_keyboard for btn in row]
    assert any("به همه" in l for l in labels), "missing «به همهٔ ختم‌ها» option"
    # only the 2 ACTIVE khatms are offered, not the cancelled one
    assert sum(1 for l in labels if l.startswith("🔹")) == 2


@pytest.mark.asyncio
async def test_new_broadcast_pushes_searchable_code_to_admin(monkeypatch):
    sent = []

    async def fake_notify(text):
        sent.append(text)

    monkeypatch.setattr(cb, "notify_super_admins", fake_notify)
    item = SimpleNamespace(
        id=uuid4(), body="پیام آزمایشی", media_type="text", audience_count=7,
    )

    await cb._notify_admins_of_broadcast_request(
        item=item, creator_name="خانم رضایی", scope_title="ختم صلوات",
    )

    assert len(sent) == 1
    assert str(item.id) in sent[0]
    assert "خانم رضایی" in sent[0] and "ختم صلوات" in sent[0]
    assert "پنل ادمین" in sent[0] and "جست‌وجو" in sent[0]
