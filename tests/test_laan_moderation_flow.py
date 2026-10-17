"""Test custom La'an moderation flag pending_lan_approval and review flow."""

import pytest
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.khatm import repository as khatm_repo


def test_khatm_model_has_pending_lan_approval():
    khatm = Khatm(
        title="ختم لعن تستی",
        template_type=KhatmTemplateType.SALAWAT,
        khatm_type=KhatmTypeEnum.OPEN,
    )
    assert hasattr(khatm, "pending_lan_approval")
    assert khatm.pending_lan_approval is False or khatm.pending_lan_approval is None


@pytest.mark.asyncio
async def test_khatm_repo_create_with_pending_lan_approval(monkeypatch):
    calls = []

    class DummySession:
        def add(self, item):
            calls.append(item)

        async def flush(self):
            pass

    session = DummySession()
    khatm = await khatm_repo.create(
        session,
        creator_user_id="00000000-0000-0000-0000-000000000001",
        title="ختم لعن سفارشی",
        template_type=KhatmTemplateType.SALAWAT,
        khatm_type=KhatmTypeEnum.OPEN,
        description="اللهم العن اول ظالم ظلم حق محمد وآل محمد",
        pending_lan_approval=True,
    )

    assert khatm.pending_lan_approval is True
    assert khatm.description == "اللهم العن اول ظالم ظلم حق محمد وآل محمد"


def test_sql_compiles_pending_lan_approval_queries():
    from sqlalchemy import func, or_, select
    from khatmsaz.modules.khatm_category.models import KhatmCategory, KhatmCategoryGroup

    stmt1 = select(func.count()).select_from(Khatm).where(Khatm.pending_lan_approval.is_(True))
    compiled1 = str(stmt1.compile())
    assert "pending_lan_approval" in compiled1

    stmt2 = select(Khatm).where(
        or_(
            KhatmCategory.group == KhatmCategoryGroup.LAAN,
            Khatm.pending_lan_approval.is_(True),
        )
    )
    compiled2 = str(stmt2.compile())
    assert "pending_lan_approval" in compiled2


@pytest.mark.asyncio
async def test_khatm_repo_review_laan_khatm():
    dummy_khatm = Khatm(
        title="ختم لعن سفارشی",
        template_type=KhatmTemplateType.SALAWAT,
        khatm_type=KhatmTypeEnum.OPEN,
        description="متن لعن آزمایشی",
        status=KhatmStatus.DRAFT,
        pending_lan_approval=True,
    )

    class DummySession:
        async def get(self, model, ident):
            return dummy_khatm

        async def flush(self):
            pass

    session = DummySession()
    reviewed = await khatm_repo.review_laan_khatm(
        session,
        dummy_khatm.id,
        approved=True,
        updated_description="متن اصلاح‌شده",
    )

    assert reviewed is not None
    assert reviewed.status == KhatmStatus.ACTIVE
    assert reviewed.pending_lan_approval is False
    assert reviewed.description == "متن اصلاح‌شده"

