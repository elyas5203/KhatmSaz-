from types import SimpleNamespace

import pytest

from khatmsaz.modules.khatm_category import service


@pytest.mark.asyncio
async def test_category_update_persists_wizard_sort_order(monkeypatch):
    category = SimpleNamespace(id="category-id")
    captured = {}

    async def get_by_id(session, category_id):
        return category

    async def update(session, row, **kwargs):
        captured.update(kwargs)
        return row

    monkeypatch.setattr(service.repository, "get_by_id", get_by_id)
    monkeypatch.setattr(service.repository, "update", update)

    await service.update(
        object(), "category-id", title="زیارت عاشورا", body_text=None,
        source_note=None, devotional_slug="ziyarat-ashura", sort_order=15,
    )

    assert captured["sort_order"] == 15


@pytest.mark.asyncio
async def test_category_sort_order_cannot_be_negative(monkeypatch):
    monkeypatch.setattr(
        service.repository, "get_by_id",
        lambda *args, **kwargs: None,
    )
    with pytest.raises(ValueError, match="sort order"):
        await service.create(
            object(), group="DUA", title="دعای عهد", body_text=None,
            source_note=None, sort_order=-1,
        )


@pytest.mark.asyncio
async def test_reposition_moves_exactly_to_requested_wizard_position(monkeypatch):
    group = SimpleNamespace(value="DUA")
    first = SimpleNamespace(id="first", group=group, sort_order=1)
    second = SimpleNamespace(id="second", group=group, sort_order=2)
    ashura = SimpleNamespace(id="ashura", group=group, sort_order=3)
    saved = []

    async def get_by_id(session, category_id):
        return ashura

    async def list_all(session):
        return [first, second, ashura]

    async def set_sort_orders(session, ordered):
        saved.extend(item.id for item in ordered)
        for index, item in enumerate(ordered, start=1):
            item.sort_order = index

    monkeypatch.setattr(service.repository, "get_by_id", get_by_id)
    monkeypatch.setattr(service.repository, "list_all", list_all)
    monkeypatch.setattr(service.repository, "set_sort_orders", set_sort_orders)

    await service.reposition(object(), "ashura", 2)

    assert saved == ["first", "ashura", "second"]
    assert ashura.sort_order == 2
