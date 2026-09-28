"""R1 (owner 2026-09-28): wizard prompts must replace each other instead of
piling up in the chat. `_wiz` deletes the previously-sent bot prompt, sends the
new one, and remembers its id — and a failed delete never blocks the new prompt.
"""
import pytest

from khatmsaz.bot.handlers.create_khatm import _wiz


class FakeBot:
    def __init__(self, fail_delete=False):
        self.deleted = []
        self.fail_delete = fail_delete

    async def delete_message(self, chat_id, mid):
        if self.fail_delete:
            raise RuntimeError("too old")
        self.deleted.append((chat_id, mid))


class FakeSent:
    def __init__(self, mid):
        self.message_id = mid


class FakeMessage:
    def __init__(self, bot):
        self.bot = bot
        self.chat = type("C", (), {"id": 555})()
        self.sent = []
        self._next = 100

    async def answer(self, text, reply_markup=None):
        self._next += 1
        self.sent.append(text)
        return FakeSent(self._next)


class FakeState:
    def __init__(self, data=None):
        self._d = dict(data or {})

    async def get_data(self):
        return dict(self._d)

    async def update_data(self, **kw):
        self._d.update(kw)


@pytest.mark.asyncio
async def test_wiz_first_call_just_sends_and_tracks_id():
    bot = FakeBot()
    msg = FakeMessage(bot)
    state = FakeState()
    await _wiz(msg, state, "step 1")
    assert msg.sent == ["step 1"]
    assert bot.deleted == []  # nothing to delete yet
    assert (await state.get_data())["_wiz_mid"] == 101


@pytest.mark.asyncio
async def test_wiz_deletes_previous_prompt():
    bot = FakeBot()
    msg = FakeMessage(bot)
    state = FakeState({"_wiz_mid": 101})
    await _wiz(msg, state, "step 2")
    assert bot.deleted == [(555, 101)]
    assert (await state.get_data())["_wiz_mid"] == 101


@pytest.mark.asyncio
async def test_wiz_failed_delete_still_sends():
    bot = FakeBot(fail_delete=True)
    msg = FakeMessage(bot)
    state = FakeState({"_wiz_mid": 101})
    await _wiz(msg, state, "step 3")
    assert msg.sent == ["step 3"]  # send happened despite delete failure
    assert (await state.get_data())["_wiz_mid"] == 101
