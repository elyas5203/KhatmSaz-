"""R1 (owner 2026-09-28): wizard prompts must replace each other instead of
piling up in the chat. `_wiz` deletes the previously-sent bot prompt, sends the
new one, and remembers its id — and a failed delete never blocks the new prompt.
"""
import pytest

from khatmsaz.bot.handlers.create_khatm import _wiz


class FakeBot:
    def __init__(self, fail_delete=False):
        self.deleted = []
        self.edited = []
        self.fail_delete = fail_delete

    async def delete_message(self, chat_id, mid):
        if self.fail_delete:
            raise RuntimeError("too old")
        self.deleted.append((chat_id, mid))

    async def edit_message_text(self, *, chat_id, message_id, text, reply_markup=None):
        if self.fail_delete:
            raise RuntimeError("cannot edit")
        self.edited.append((chat_id, message_id, text))


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
    assert bot.deleted == []
    assert bot.edited == [(555, 101, "step 2")]
    assert (await state.get_data())["_wiz_mid"] == 101


@pytest.mark.asyncio
async def test_wiz_failed_delete_still_sends():
    bot = FakeBot(fail_delete=True)
    msg = FakeMessage(bot)
    state = FakeState({"_wiz_mid": 101})
    await _wiz(msg, state, "step 3")
    assert msg.sent == ["step 3"]  # send happened despite delete failure
    assert (await state.get_data())["_wiz_mid"] == 101


@pytest.mark.asyncio
async def test_wiz_deletes_tracked_intro_with_next_completed_step():
    bot = FakeBot()
    msg = FakeMessage(bot)
    state = FakeState({"_wiz_mid": 101, "_wiz_extra_mids": [102]})

    await _wiz(msg, state, "next question")

    assert bot.deleted == [(555, 102)]
    assert bot.edited == [(555, 101, "next question")]
    assert (await state.get_data())["_wiz_extra_mids"] == []


@pytest.mark.asyncio
async def test_wiz_can_keep_intro_beside_title_until_answered():
    bot = FakeBot()
    msg = FakeMessage(bot)
    state = FakeState({"_wiz_mid": 101, "_wiz_extra_mids": [102]})

    await _wiz(msg, state, "title question", keep_extra=True)

    assert bot.deleted == []
    assert bot.edited == [(555, 101, "title question")]
    assert (await state.get_data())["_wiz_extra_mids"] == [102]


@pytest.mark.asyncio
async def test_wiz_separates_progress_card_from_current_question():
    bot = FakeBot()
    msg = FakeMessage(bot)
    state = FakeState({"_wiz_mid": 55, "lang": "fa", "template_type": "QURAN_PAGE"})

    await _wiz(msg, state, "سؤال مرحلهٔ بعد")

    assert bot.deleted == [(555, 55)]
    assert len(msg.sent) == 2
    assert "انتخاب‌های شما تا اینجا" in msg.sent[0]
    assert msg.sent[1] == "سؤال مرحلهٔ بعد"
    data = await state.get_data()
    assert data["_wiz_summary_mid"] == 101
    assert data["_wiz_mid"] == 102


@pytest.mark.asyncio
async def test_wiz_does_not_recreate_unchanged_summary():
    bot = FakeBot()
    msg = FakeMessage(bot)
    state = FakeState({
        "_wiz_mid": 102,
        "_wiz_summary_mid": 101,
        "_wiz_summary_text": "📋 انتخاب‌های شما تا اینجا:\n• نوع ختم: قرآن",
        "_wiz_question_text": "پرسش قبلی",
        "lang": "fa",
        "template_type": "QURAN_PAGE",
    })

    await _wiz(msg, state, "پرسش بعدی")

    assert msg.sent == []
    assert bot.edited == [(555, 102, "پرسش بعدی")]
    assert (await state.get_data())["_wiz_summary_mid"] == 101
