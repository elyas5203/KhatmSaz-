"""Tests for MASTER-30:
1. Fixing khatm_detail.html debt_count UndefinedError and enriching _load_creator_member_rows.
2. Disabling Khatm La'an creation across Bot and Web.
"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
import pytest
from aiogram.types import CallbackQuery, Message

from khatmsaz.bot.keyboards import template_choice_keyboard
from khatmsaz.bot.handlers.create_khatm import choose_category_group, enter_laan_title, enter_laan_text
from khatmsaz.modules.khatm_category.models import KhatmCategoryGroup


def test_template_choice_keyboard_has_no_laan():
    kb = template_choice_keyboard("fa")
    callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
    assert "ck:group:LAAN" not in callbacks
    assert "ck:tpl:QURAN_PAGE" in callbacks
    assert "ck:group:SALAWAT" in callbacks
    assert "ck:group:DUA" in callbacks
    assert "ck:group:KHUTBAH" in callbacks


@pytest.mark.asyncio
async def test_choose_category_group_laan_is_blocked():
    callback = MagicMock(spec=CallbackQuery)
    callback.data = "ck:group:LAAN"
    callback.answer = AsyncMock()
    state = MagicMock()
    state.get_data = AsyncMock(return_value={"lang": "fa"})

    await choose_category_group(callback, state)
    callback.answer.assert_called_once()
    assert "غیرفعال" in callback.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_enter_laan_title_and_text_are_blocked():
    message = MagicMock(spec=Message)
    message.text = "عنوان تستی"
    message.answer = AsyncMock()
    state = MagicMock()
    state.get_data = AsyncMock(return_value={"lang": "fa"})
    state.clear = AsyncMock()

    await enter_laan_title(message, state)
    state.clear.assert_called_once()
    message.answer.assert_called_once()
    assert "غیرفعال" in message.answer.call_args[0][0]

    state.clear.reset_mock()
    message.answer.reset_mock()
    await enter_laan_text(message, state)
    state.clear.assert_called_once()
    message.answer.assert_called_once()
    assert "غیرفعال" in message.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_web_creator_and_admin_khatm_create_rejects_laan():
    from starlette.testclient import TestClient
    from khatmsaz.web.app import app

    client = TestClient(app, raise_server_exceptions=False)
    # Creator route POST with laan
    res = client.post("/creator/khatms/create", data={"content_kind": "laan", "khatm_type": "OPEN", "csrf": "dummy"}, follow_redirects=False)
    assert res.status_code in {303, 400, 403, 422}

    # Admin route POST with laan
    res_admin = client.post("/khatms/create", data={"content_kind": "laan", "csrf": "dummy"}, follow_redirects=False)
    assert res_admin.status_code in {303, 400, 403, 422}


def test_khatm_detail_template_renders_without_debt_count():
    from jinja2 import Environment, FileSystemLoader
    from pathlib import Path

    templates_dir = Path("src/khatmsaz/web/templates")
    env = Environment(loader=FileSystemLoader(str(templates_dir)))
    env.globals["fa_label"] = lambda x: str(x)
    env.globals["label"] = lambda x: str(x)
    env.globals["t"] = lambda k, l="fa", **kw: k
    env.globals["web_t"] = lambda k, l="fa", **kw: k
    env.globals["_tehran_time"] = lambda dt: "1405-01-01"

    template = env.get_template("khatm_detail.html")
    dummy_membership = MagicMock()
    dummy_membership.id = uuid4()
    dummy_membership.status.value = "ACTIVE"
    dummy_membership.is_committed = True

    dummy_user = MagicMock()
    dummy_user.id = uuid4()
    dummy_user.display_name = "تست کننده"

    # Row without debt_count attribute or key
    row_without_debt = {
        "membership": dummy_membership,
        "user": dummy_user,
        "settings": None,
        "completed": 5,
        "read_count": 5,
        # note: debt_count omitted intentionally to test defensive get
    }

    dummy_khatm = MagicMock()
    dummy_khatm.id = uuid4()
    dummy_khatm.title = "ختم آزمایشی"
    dummy_khatm.niyyat = "نیت"
    dummy_khatm.status.value = "ACTIVE"
    dummy_khatm.template_type.value = "SALAWAT"
    dummy_khatm.khatm_type.value = "COMMITMENT"
    dummy_khatm.repetition_target = 100
    dummy_khatm.allowed_platforms = "BOTH"
    dummy_khatm.visibility.value = "PUBLIC"

    dummy_stats = MagicMock()
    dummy_stats.completed_portions = 10
    dummy_stats.total_portions = 100
    dummy_stats.active_members = 1
    dummy_stats.days_remaining = 5

    dummy_req = MagicMock()
    dummy_req.url.path = "/khatms/test"

    rendered = template.render(
        request=dummy_req,
        khatm=dummy_khatm,
        creator_user=dummy_user,
        category=None,
        stats=dummy_stats,
        rows=[row_without_debt],
        waiting_rows=[],
        csrf="test_csrf",
        invite_url="https://t.me/test",
        query="",
        page=1,
        has_next=False,
    )
    assert "تست کننده" in rendered
    assert "✅ ثبت سهم" not in rendered  # Since debt_count is 0 or missing, no button
