from contextlib import asynccontextmanager

import pytest
from fastapi.responses import JSONResponse

import khatmsaz.web.app as web_app


class _HealthySession:
    async def execute(self, _statement):
        return object()


@pytest.mark.asyncio
async def test_health_reports_database_ready(monkeypatch):
    @asynccontextmanager
    async def healthy_scope():
        yield _HealthySession()

    monkeypatch.setattr(web_app, "session_scope", healthy_scope)

    assert await web_app.health() == {"status": "ok", "database": "ok"}


@pytest.mark.asyncio
async def test_health_fails_closed_without_leaking_database_error(monkeypatch):
    @asynccontextmanager
    async def failed_scope():
        raise RuntimeError("postgresql://secret@internal-host/database")
        yield  # pragma: no cover - makes this an async context manager

    monkeypatch.setattr(web_app, "session_scope", failed_scope)

    response = await web_app.health()

    assert isinstance(response, JSONResponse)
    assert response.status_code == 503
    assert response.body == b'{"status":"unavailable","database":"unavailable"}'
    assert b"secret" not in response.body
