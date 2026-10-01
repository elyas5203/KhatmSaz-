"""The owner temporarily disabled the public web invitation page."""

import pytest
from httpx import ASGITransport, AsyncClient

from khatmsaz.web.app import app


@pytest.mark.asyncio
async def test_public_join_page_is_disabled_for_every_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        page = await client.get("/join/any-old-or-new-token")

    assert page.status_code == 404
    assert "فعلاً غیرفعال است" in page.text
