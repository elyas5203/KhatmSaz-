"""Guards against the raw-slug / Persian-on-other-language class of bug the
owner hit in live QA (e.g. «button.confirm», «my_khatms.button.leave» showing
literally). Two invariants:
  1. every i18n key defines all three languages (fa/ar/en);
  2. every literal t("...")/web_t("...") key referenced in bot/web/module code
     actually exists — a missing key renders the raw slug to the user.
"""
import re
from pathlib import Path

from khatmsaz.i18n import _STRINGS

_SRC = Path(__file__).resolve().parents[1] / "src" / "khatmsaz"
_KEY_CALL = re.compile(r'\b(?:web_t|t)\(\s*"([a-z0-9_][a-z0-9_.]+)"')


def test_every_i18n_key_has_all_three_languages():
    incomplete = {
        key: [lang for lang in ("fa", "ar", "en") if not value.get(lang)]
        for key, value in _STRINGS.items()
        if not (value.get("fa") and value.get("ar") and value.get("en"))
    }
    assert not incomplete, f"i18n keys missing a language (shows wrong language to users): {incomplete}"


def test_no_literal_t_key_is_missing():
    known = set(_STRINGS.keys())
    missing: dict[str, list[str]] = {}
    for path in _SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for key in _KEY_CALL.findall(text):
            if key not in known:
                missing.setdefault(key, []).append(path.name)
    assert not missing, f"t()/web_t() references to undefined i18n keys (render raw slug): {missing}"
