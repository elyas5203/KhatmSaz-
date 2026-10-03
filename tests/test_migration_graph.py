from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


def _script_directory() -> ScriptDirectory:
    root = Path(__file__).resolve().parents[1]
    config = Config()
    config.set_main_option("script_location", str(root / "migrations"))
    return ScriptDirectory.from_config(config)


def test_bot_instance_migrations_are_ordered_before_intro_image() -> None:
    """A fresh database must create bot_instances before referencing it."""
    script = _script_directory()

    joined_via_bot = script.get_revision("b8c9d0e1f2b4")
    redesign_merge = script.get_revision("mrg2026092801")
    final = script.get_revision("fin2026092804")
    rotating = script.get_revision("rot2026092805")

    assert joined_via_bot is not None
    assert joined_via_bot.down_revision == "b7c8d9e0f1a2"
    assert redesign_merge is not None
    assert "506f73c6ae72" in redesign_merge._normalized_down_revisions
    assert final is not None
    assert final.down_revision == "bii2026092803"
    assert rotating is not None
    assert rotating.down_revision == "fin2026092804"
    broadcast = script.get_revision("broadcast2026092901")
    assert broadcast is not None
    assert broadcast.down_revision == "rot2026092805"
    filters = script.get_revision("broadcastfilters2026093001")
    assert filters is not None
    assert filters.down_revision == "broadcast2026092901"
    weekdays = script.get_revision("schedweekdays2026100101")
    assert weekdays is not None
    assert weekdays.down_revision == "broadcastfilters2026093001"
    salawat_asset = script.get_revision("devsalawat2026100102")
    assert salawat_asset is not None
    assert salawat_asset.down_revision == "schedweekdays2026100101"
    occurrences = script.get_revision("occ2026100301")
    assert occurrences is not None
    assert occurrences.down_revision == "devsalawat2026100102"
    policy = script.get_revision("policy2026100302")
    assert policy is not None
    assert policy.down_revision == "occ2026100301"
    assert script.get_heads() == ["policy2026100302"]
