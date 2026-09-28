"""N1 (owner 2026-09-28): a line-by-line audit of the i18n registry. Rather
than a one-off pass, these guards keep the registry healthy forever:

- no duplicate keys (a dup silently overrides the earlier one — a real bug),
- every key present in fa/ar/en (also covered by test_i18n_coverage),
- no empty strings,
- placeholders (`{name}`) identical across languages so `t(...).format(**kw)`
  can never raise a KeyError or silently drop an interpolation,
- values are strings.
"""
import ast
import pathlib
import re

from khatmsaz.i18n import _STRINGS, SUPPORTED_LANGUAGES

_PH = re.compile(r"\{([a-zA-Z0-9_]+)\}")
_I18N_FILE = pathlib.Path(__file__).resolve().parents[1] / "src" / "khatmsaz" / "i18n" / "__init__.py"


def test_no_duplicate_keys_in_source():
    """The dict literal must not define the same key twice (Python would keep
    only the last, hiding the earlier translation)."""
    tree = ast.parse(_I18N_FILE.read_text(encoding="utf-8"))
    dict_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict) and any(
            isinstance(k, ast.Constant) and k.value == "menu.today" for k in node.keys
        ):
            dict_node = node
            break
    assert dict_node is not None, "could not locate the _STRINGS dict literal"
    keys = [k.value for k in dict_node.keys if isinstance(k, ast.Constant)]
    dupes = {k for k in keys if keys.count(k) > 1}
    assert not dupes, f"duplicate i18n keys defined twice: {sorted(dupes)}"


def test_all_langs_present_and_nonempty():
    problems = []
    for key, val in _STRINGS.items():
        for lang in SUPPORTED_LANGUAGES:
            if lang not in val:
                problems.append(f"{key}:{lang} missing")
            elif not isinstance(val[lang], str):
                problems.append(f"{key}:{lang} not a string")
            elif not val[lang].strip():
                problems.append(f"{key}:{lang} empty")
    assert not problems, problems


def test_placeholders_match_across_languages():
    problems = []
    for key, val in _STRINGS.items():
        sets = {l: set(_PH.findall(val[l])) for l in SUPPORTED_LANGUAGES if isinstance(val.get(l), str)}
        base = sets.get("fa", set())
        for lang, phs in sets.items():
            if phs != base:
                problems.append(f"{key}: fa={sorted(base)} vs {lang}={sorted(phs)}")
    assert not problems, problems
