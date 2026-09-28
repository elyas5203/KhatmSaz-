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

    assert joined_via_bot is not None
    assert joined_via_bot.down_revision == "b7c8d9e0f1a2"
    assert redesign_merge is not None
    assert "506f73c6ae72" in redesign_merge._normalized_down_revisions
    assert final is not None
    assert final.down_revision == "bii2026092803"
    assert script.get_heads() == ["fin2026092804"]
