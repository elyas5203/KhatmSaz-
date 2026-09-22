"""BACKLOG.md §18 (owner, 2026-09-21): "ختم‌های من" should be a hierarchical
menu — three top branches (created / joined / finished), each split by
content type (Quran/Salawat/Dua/La'an) — instead of one long text dump.
This exercises the tree builder directly against real Postgres data: one
created Quran khatm, one joined Salawat (plain) khatm, and one joined Dua
khatm (via a real `KhatmCategory` row), and checks they land in the right
branch/category buckets."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import delete

from khatmsaz.bot.handlers import my_khatms as my_khatms_handlers
from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.khatm_category import service as category_service
from khatmsaz.modules.khatm_category.models import KhatmCategory
from khatmsaz.modules.participation import repository as participation_repository


@pytest.mark.integration
@pytest.mark.asyncio
async def test_tree_groups_by_branch_and_content_category():
    creator_id, member_id = new_id(), new_id()
    quran_id, salawat_id, dua_id = new_id(), new_id(), new_id()

    async with session_scope() as session:
        session.add_all([User(id=creator_id), User(id=member_id)])
        dua_category = await category_service.create(
            session, group="DUA", title="دعای تست سلسله‌مراتب", body_text=None, source_note=None,
        )
        session.add_all([
            Khatm(
                id=quran_id, creator_user_id=creator_id, title="قرآن سلسله‌مراتبی",
                template_type=KhatmTemplateType.QURAN_PAGE, khatm_type=KhatmTypeEnum.COMMITMENT,
                status=KhatmStatus.ACTIVE,
            ),
            Khatm(
                id=salawat_id, creator_user_id=creator_id, title="صلوات سلسله‌مراتبی",
                template_type=KhatmTemplateType.SALAWAT, khatm_type=KhatmTypeEnum.OPEN,
                status=KhatmStatus.ACTIVE,
            ),
            Khatm(
                id=dua_id, creator_user_id=creator_id, title="دعای سلسله‌مراتبی",
                template_type=KhatmTemplateType.SALAWAT, khatm_type=KhatmTypeEnum.OPEN,
                status=KhatmStatus.ACTIVE, content_category_id=dua_category.id,
            ),
        ])
        await session.flush()

        # `creator_id` created all three; `member_id` separately joined the
        # salawat and dua ones (not the Quran one) to also populate the
        # "joined" branch.
        salawat_participation = await participation_repository.create(session, salawat_id, member_id, is_committed=False)
        dua_participation = await participation_repository.create(session, dua_id, member_id, is_committed=False)

        creator_tree = await my_khatms_handlers._build_my_khatms_tree(session, creator_id, "fa")
        member_tree = await my_khatms_handlers._build_my_khatms_tree(session, member_id, "fa")

        assert set(creator_tree["created"].keys()) == {"quran", "salawat", "dua"}
        assert len(creator_tree["created"]["quran"]) == 1
        assert len(creator_tree["created"]["salawat"]) == 1
        assert len(creator_tree["created"]["dua"]) == 1
        assert creator_tree["joined"] == {}
        assert creator_tree["finished"] == {}

        assert set(member_tree["joined"].keys()) == {"salawat", "dua"}
        assert len(member_tree["joined"]["salawat"]) == 1
        assert len(member_tree["joined"]["dua"]) == 1
        assert member_tree["created"] == {}

        # Rendering shouldn't blow up at any of the three levels.
        root_text, root_kb = my_khatms_handlers._render_my_khatms_root(creator_tree, "fa")
        assert len(root_kb.inline_keyboard) == 3
        branch_text, branch_kb = my_khatms_handlers._render_my_khatms_branch(creator_tree, "created", "fa")
        assert len(branch_kb.inline_keyboard) == 4  # 3 categories + back
        category_text, category_kb = my_khatms_handlers._render_my_khatms_category(creator_tree, "created", "quran", "fa")
        assert "قرآن سلسله‌مراتبی" in category_text
        assert len(category_kb.inline_keyboard) == 2  # 1 item's action row + back

        await session.execute(delete(type(salawat_participation)).where(
            type(salawat_participation).id.in_([salawat_participation.id, dua_participation.id])
        ))
        await session.execute(delete(Khatm).where(Khatm.id.in_([quran_id, salawat_id, dua_id])))
        await session.execute(delete(KhatmCategory).where(KhatmCategory.id == dua_category.id))
        await session.execute(delete(User).where(User.id.in_([creator_id, member_id])))
