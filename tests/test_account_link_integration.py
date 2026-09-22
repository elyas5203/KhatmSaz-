"""Real PostgreSQL self-service platform/account linking flow."""

import pytest
from sqlalchemy import delete, select

from khatmsaz.config import get_settings
from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.account_merge.models import AccountMerge
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User, UserStatus
from khatmsaz.modules.phone import service
from khatmsaz.modules.phone.models import OtpChallenge, PhoneClaim
from khatmsaz.modules.settings.models import Gender, UserSettings


@pytest.mark.integration
@pytest.mark.asyncio
async def test_new_bale_identity_moves_to_existing_profile_after_otp(monkeypatch):
    monkeypatch.setenv("OTP_HMAC_SECRET", "account-link-integration-secret")
    monkeypatch.setenv("DEV_OTP", "true")
    get_settings.cache_clear()
    target_id, source_id = new_id(), new_id()
    async with session_scope() as session:
        target = User(id=target_id, display_name="کاربر قدیمی")
        source = User(id=source_id)
        session.add_all(
            [
                target,
                source,
                PlatformIdentity(
                    id=new_id(), user_id=target_id, platform=Platform.TELEGRAM, subject="tg-old"
                ),
                PlatformIdentity(
                    id=new_id(), user_id=source_id, platform=Platform.BALE, subject="bale-new"
                ),
                UserSettings(
                    user_id=target_id,
                    contact_phone="09990001234",
                    province="تهران",
                    city="تهران",
                    gender=Gender.MALE,
                ),
            ]
        )
        await session.flush()

        found, challenge, code = await service.request_account_link_challenge(
            session, source_user_id=source_id, e164="+989990001234"
        )
        assert found.id == target_id
        assert code and len(code) == 6
        linked = await service.complete_account_link(
            session,
            source_user_id=source_id,
            target_user_id=target_id,
            challenge_id=challenge.id,
            code=code,
            platform=Platform.BALE,
            subject="bale-new",
        )
        assert linked.id == target_id
        bale_identity = await session.scalar(
            select(PlatformIdentity).where(
                PlatformIdentity.platform == Platform.BALE,
                PlatformIdentity.subject == "bale-new",
            )
        )
        assert bale_identity.user_id == target_id
        assert source.status == UserStatus.MERGED
        assert source.merged_into_id == target_id
        merge = await session.scalar(
            select(AccountMerge).where(AccountMerge.loser_user_id == source_id)
        )
        assert merge.winner_user_id == target_id
        assert merge.verified_e164 == "+989990001234"

        await session.execute(delete(AccountMerge).where(AccountMerge.loser_user_id == source_id))
        await session.execute(delete(PhoneClaim).where(PhoneClaim.user_id == target_id))
        await session.execute(delete(OtpChallenge).where(OtpChallenge.user_id == target_id))
        await session.execute(
            delete(PlatformIdentity).where(PlatformIdentity.user_id.in_([target_id, source_id]))
        )
        await session.execute(delete(UserSettings).where(UserSettings.user_id == target_id))
        await session.execute(delete(User).where(User.id.in_([source_id, target_id])))
    get_settings.cache_clear()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_nonempty_provisional_account_cannot_be_silently_merged(monkeypatch):
    monkeypatch.setenv("OTP_HMAC_SECRET", "account-link-integration-secret")
    get_settings.cache_clear()
    target_id, source_id = new_id(), new_id()
    async with session_scope() as session:
        session.add_all(
            [
                User(id=target_id),
                User(id=source_id, display_name="حساب استفاده‌شده"),
                UserSettings(user_id=target_id, contact_phone="09120000000"),
            ]
        )
        await session.flush()
        with pytest.raises(service.OtpError, match="no longer empty"):
            await service.request_account_link_challenge(
                session, source_user_id=source_id, e164="09120000000"
            )
        await session.execute(delete(UserSettings).where(UserSettings.user_id == target_id))
        await session.execute(delete(User).where(User.id.in_([source_id, target_id])))
    get_settings.cache_clear()
