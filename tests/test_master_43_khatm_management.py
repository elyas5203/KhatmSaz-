"""Tests for MASTER-43: Admin Khatm Management, Direct Ownership Transfer & Intelligent Status Notifications."""

import pytest
from unittest.mock import AsyncMock, patch
from contextlib import asynccontextmanager
from uuid import uuid4

from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTypeEnum, KhatmVisibility
from khatmsaz.modules.identity.models import User, PlatformIdentity
from khatmsaz.modules.khatm_workflow.service import direct_transfer_khatm, KhatmTransferError


class DummySession:
    """Mock async session for testing direct transfer logic."""
    def __init__(self, khatm, users=None):
        self.khatm = khatm
        self.users = users or {}
        self.added = []

    async def get(self, model, ident):
        if model == Khatm and ident == self.khatm.id:
            return self.khatm
        if model == User:
            return self.users.get(ident)
        return None

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        pass


@pytest.mark.asyncio
async def test_direct_transfer_khatm_success():
    old_creator_id = uuid4()
    new_creator_id = uuid4()
    admin_id = uuid4()
    khatm_id = uuid4()

    khatm = Khatm(
        id=khatm_id,
        creator_user_id=old_creator_id,
        title="ختم صلوات تستی",
        template_type="SALAWAT",
        khatm_type=KhatmTypeEnum.COMMITMENT,
        status=KhatmStatus.ACTIVE,
        visibility=KhatmVisibility.PRIVATE,
    )

    session = DummySession(khatm)

    with patch("khatmsaz.modules.khatm.service.get_khatm_for_update", AsyncMock(return_value=khatm)), \
         patch("khatmsaz.modules.invitation.service.revoke_all_for_khatm", AsyncMock(return_value=1)) as mock_revoke, \
         patch("khatmsaz.modules.invitation.service.create_invitation", AsyncMock(return_value="new_raw_token")) as mock_create:

        updated_khatm, orig_creator, new_token = await direct_transfer_khatm(
            session,
            khatm_id=khatm_id,
            new_creator_user_id=new_creator_id,
            admin_user_id=admin_id,
        )

        assert updated_khatm.creator_user_id == new_creator_id
        assert updated_khatm.transferred_from_user_id == old_creator_id
        assert updated_khatm.transfer_request_status == "DIRECT_TRANSFER"
        assert updated_khatm.transferred_to_admin_at is not None
        assert orig_creator == old_creator_id
        assert new_token == "new_raw_token"

        mock_revoke.assert_awaited_once_with(session, khatm_id)
        mock_create.assert_awaited_once_with(session, khatm_id, new_creator_id)


@pytest.mark.asyncio
async def test_direct_transfer_khatm_same_creator_error():
    creator_id = uuid4()
    khatm_id = uuid4()

    khatm = Khatm(
        id=khatm_id,
        creator_user_id=creator_id,
        title="ختم صلوات",
        template_type="SALAWAT",
        khatm_type=KhatmTypeEnum.COMMITMENT,
        status=KhatmStatus.ACTIVE,
    )

    session = DummySession(khatm)

    with patch("khatmsaz.modules.khatm.service.get_khatm_for_update", AsyncMock(return_value=khatm)):
        with pytest.raises(KhatmTransferError, match="user is already the creator of this khatm"):
            await direct_transfer_khatm(
                session,
                khatm_id=khatm_id,
                new_creator_user_id=creator_id,
                admin_user_id=uuid4(),
            )


@pytest.mark.asyncio
async def test_notify_status_update_messages():
    from khatmsaz.web.app import _notify_khatm_status_update

    mock_notify = AsyncMock()
    creator_id = uuid4()
    member_id = uuid4()

    creator_ident = PlatformIdentity(user_id=creator_id, platform="TELEGRAM", subject="111")
    member_ident = PlatformIdentity(user_id=member_id, platform="TELEGRAM", subject="222")

    dummy_session = AsyncMock()
    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    with patch("khatmsaz.bot.notify_adapter.get_notify_fn", return_value=mock_notify), \
         patch("khatmsaz.modules.identity.service.list_identities_for_user") as mock_list_idents, \
         patch("khatmsaz.web.app.session_scope", mock_scope):

        async def _mock_idents(session, uid):
            return [creator_ident] if uid == creator_id else [member_ident]
        mock_list_idents.side_effect = _mock_idents

        # Test COMPLETED notification
        await _notify_khatm_status_update(
            khatm_title="ختم عاشورا",
            target_status_val=KhatmStatus.COMPLETED.value,
            creator_id=creator_id,
            active_member_user_ids=[member_id],
        )

        assert mock_notify.await_count == 2
        # Creator message contains "تکمیل دورهٔ ختم"
        creator_call = mock_notify.await_args_list[0]
        assert "تکمیل" in creator_call[0][2]
        assert "ختم عاشورا" in creator_call[0][2]

        # Member message contains "پایان دورهٔ ختم"
        member_call = mock_notify.await_args_list[1]
        assert "پایان دورهٔ ختم" in member_call[0][2]
        assert "ختم عاشورا" in member_call[0][2]


@pytest.mark.asyncio
async def test_notify_transfer_parties():
    from khatmsaz.web.app import _notify_transfer_parties

    mock_notify = AsyncMock()
    old_creator_id = uuid4()
    new_creator_id = uuid4()

    old_ident = PlatformIdentity(user_id=old_creator_id, platform="TELEGRAM", subject="333")
    new_ident = PlatformIdentity(user_id=new_creator_id, platform="TELEGRAM", subject="444")

    dummy_session = AsyncMock()
    @asynccontextmanager
    async def mock_scope():
        yield dummy_session

    with patch("khatmsaz.bot.notify_adapter.get_notify_fn", return_value=mock_notify), \
         patch("khatmsaz.modules.identity.service.list_identities_for_user") as mock_list_idents, \
         patch("khatmsaz.web.app.session_scope", mock_scope):

        async def _mock_idents(session, uid):
            return [old_ident] if uid == old_creator_id else [new_ident]
        mock_list_idents.side_effect = _mock_idents

        await _notify_transfer_parties(
            khatm_title="ختم صلوات برای فرج",
            old_creator_id=old_creator_id,
            new_creator_id=new_creator_id,
        )

        assert mock_notify.await_count == 2
        assert "تغییر مدیریت ختم" in mock_notify.await_args_list[0][0][2]
        assert "واگذاری مدیریت ختم" in mock_notify.await_args_list[1][0][2]


def test_khatm_detail_template_contains_new_controls():
    with open("src/khatmsaz/web/templates/khatm_detail.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Verify status select exists with standard statuses
    assert '<select name="status"' in content
    assert '<option value="ACTIVE"' in content
    assert '<option value="COMPLETED"' in content
    assert '<option value="CANCELLED"' in content

    # Verify direct transfer form exists
    assert 'action="/khatms/{{ khatm.id }}/transfer/direct"' in content
    assert 'name="target_identifier"' in content
    assert "واگذاری مستقیم مدیریت ختم به کاربر دیگر" in content

    # Verify status changed and direct transferred alerts exist
    assert "status_changed" in content
    assert "direct_transferred" in content
    assert "{% if error %}" in content
