import asyncio
from khatmsaz.core.db import session_scope
from khatmsaz.modules.khatm_category.models import KhatmCategory
from sqlalchemy import select

async def f():
    async with session_scope() as s:
        res = await s.execute(select(KhatmCategory.title, KhatmCategory.body_text))
        print("CATEGORIES:")
        for r in res.all():
            print(f"- {r[0]}: {'(HAS TEXT)' if r[1] else '(EMPTY)'}")

asyncio.run(f())
