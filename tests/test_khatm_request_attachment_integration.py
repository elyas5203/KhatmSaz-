import pytest
from sqlalchemy import delete

import khatmsaz.core.model_registry  # noqa: F401
from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm_request import service
from khatmsaz.modules.khatm_request.models import KhatmRequest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_custom_khatm_request_keeps_optional_attachment_metadata():
    user_id = new_id()
    async with session_scope() as session:
        session.add(User(id=user_id, display_name="Attachment requester"))
        await session.flush()
        request = await service.submit(
            session, user_id, "ختم دعای عهد",
            attachment_file_id="telegram-file-1",
            attachment_file_name="dua.pdf",
            attachment_mime_type="application/pdf",
            attachment_platform="TELEGRAM",
        )
        assert request.attachment_file_id == "telegram-file-1"
        assert request.attachment_file_name == "dua.pdf"
        assert request.attachment_mime_type == "application/pdf"
        await session.execute(delete(KhatmRequest).where(KhatmRequest.id == request.id))
        await session.execute(delete(User).where(User.id == user_id))
