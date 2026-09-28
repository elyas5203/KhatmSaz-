"""R11/N2 (owner 2026-09-28): the member-commitment router + keyboards must line
up — every callback_data a keyboard emits needs a handler whose filter matches,
and the module must load cleanly under the fresh-router import used at bootstrap.
"""
import importlib.util

from khatmsaz.bot import keyboards as k
from khatmsaz.bot.handlers import member_commitment as mc


def _callback_datas(kb):
    return [b.callback_data for row in kb.inline_keyboard for b in row]


def test_mode_keyboard_callbacks():
    data = _callback_datas(k.member_commitment_mode_keyboard("pid1", "fa"))
    assert "cmode:regular:pid1" in data
    assert "cmode:count:pid1" in data


def test_freq_keyboard_callbacks():
    data = _callback_datas(k.commitment_freq_keyboard("pid1", "fa"))
    assert data == ["cfreq:DAILY:pid1", "cfreq:WEEKLY:pid1", "cfreq:MONTHLY:pid1"]


def test_hour_keyboard_has_presets_and_custom():
    data = _callback_datas(k.commitment_hour_keyboard("fa"))
    assert "chour:9" in data
    assert "chour:custom" in data
    assert all(d.startswith("chour:") for d in data)


def test_count_log_keyboard_callbacks():
    data = _callback_datas(k.commitment_count_log_keyboard("pid1", "fa"))
    assert "clog:1:pid1" in data
    assert "clogc:pid1" in data
    assert "cnew:pid1" in data


def test_router_has_expected_states():
    assert hasattr(mc.CommitFlow, "entering_count")
    assert hasattr(mc.CommitFlow, "entering_log_amount")
    assert hasattr(mc.CommitFlow, "entering_times_per_period")
    assert hasattr(mc.CommitFlow, "entering_custom_time")


def test_module_loads_via_fresh_router_like_bootstrap():
    # bootstrap re-imports shared handlers with a fresh module object; make sure
    # that path works for this module (router attribute present).
    spec = importlib.util.find_spec("khatmsaz.bot.handlers.member_commitment")
    fresh = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fresh)
    assert fresh.router.name == "member_commitment"


def test_hour_keyboard_prefix_matches_handler():
    # the picker's last step reuses delivery_hour_keyboard with prefix "chour";
    # the handler filters on "chour:". Verify the emitted data matches.
    data = _callback_datas(k.delivery_hour_keyboard("chour", "fa"))
    assert all(d.startswith("chour:") for d in data)
