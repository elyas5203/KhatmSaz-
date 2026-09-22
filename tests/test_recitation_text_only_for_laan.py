"""Owner-reported bug (2026-09-21): "برای صلوات نباید متن رو از یوزر
بخواد؛ متن صلوات همیشه ثابته... اگر متن لعن/دعا/ذکر دارین فقط باید برای
لعن باشه." The creator-authored-recitation-text step in the create-khatm
wizard was firing for every SALAWAT-template khatm regardless of category
(plain Salawat, Dua, or La'an) — it should only ever fire for La'an, since
Salawat text is fixed/standard and Dua text comes from the admin-managed
devotional library, not the creator. See
`bot/handlers/create_khatm.py::_after_welcome`."""

from khatmsaz.bot.handlers.create_khatm import CreateKhatm, _after_welcome
from khatmsaz.modules.khatm.models import KhatmTemplateType
from khatmsaz.modules.khatm_category.models import KhatmCategoryGroup


class FakeState:
    def __init__(self, data):
        self.data = data
        self.state = None

    async def get_data(self):
        return self.data

    async def set_state(self, value):
        self.state = value

    async def update_data(self, **values):
        self.data.update(values)


class FakeMessage:
    def __init__(self):
        self.answers = []

    async def answer(self, text, **kwargs):
        self.answers.append((text, kwargs))


async def _run(category_group):
    state = FakeState({"template_type": KhatmTemplateType.SALAWAT.value, "category_group": category_group, "lang": "fa"})
    message = FakeMessage()
    await _after_welcome(message, state)
    return state


async def test_laan_asks_for_recitation_text():
    state = await _run(KhatmCategoryGroup.LAAN.value)
    assert state.state == CreateKhatm.entering_recitation_text


async def test_plain_salawat_does_not_ask_for_recitation_text():
    state = await _run(None)
    assert state.state != CreateKhatm.entering_recitation_text


async def test_dua_does_not_ask_for_recitation_text():
    state = await _run(KhatmCategoryGroup.DUA.value)
    assert state.state != CreateKhatm.entering_recitation_text
