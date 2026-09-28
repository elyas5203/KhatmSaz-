"""R5 (owner 2026-09-28): a commitment khatm's creator picks the TOTAL goal
from preset buttons (10/14/40/110/313/custom/unlimited); per-person share is
set by each member. Verifies the keyboard shape/callbacks."""
from khatmsaz.bot.handlers.create_khatm import _commitment_total_keyboard


def test_total_keyboard_has_presets_custom_and_unlimited():
    kb = _commitment_total_keyboard("fa")
    data = [b.callback_data for row in kb.inline_keyboard for b in row]
    assert "ck:total:10" in data
    assert "ck:total:14" in data
    assert "ck:total:40" in data
    assert "ck:total:110" in data
    assert "ck:total:313" in data
    assert "ck:total:custom" in data
    assert "ck:total:unlimited" in data
    labels = [b.text for row in kb.inline_keyboard for b in row]
    assert "10" in labels and "313" in labels


def test_total_keyboard_translates_custom_unlimited():
    for lang in ("fa", "ar", "en"):
        labels = [b.text for row in _commitment_total_keyboard(lang).inline_keyboard for b in row]
        # custom + unlimited buttons carry an emoji + localized text (non-empty)
        assert any("🔢" in l for l in labels)
        assert any("♾" in l for l in labels)
