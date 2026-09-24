import asyncio
import os
from sqlalchemy import text
from khatmsaz.core.db import engine

async def wipe_data():
    print("⚠️ WARNING: This will delete ALL data (khatms, participations, users) EXCEPT for Super Admins!")
    confirm = input("Type 'YES' to continue: ")
    if confirm != 'YES':
        print("Aborted.")
        return

    async with engine.begin() as conn:
        print("Deleting participations...")
        await conn.execute(text("DELETE FROM participations;"))
        
        print("Deleting khatms...")
        await conn.execute(text("DELETE FROM khatms;"))
        
        print("Deleting creator requests...")
        await conn.execute(text("DELETE FROM creator_requests;"))
        
        print("Deleting notifications...")
        await conn.execute(text("DELETE FROM notifications;"))
        
        print("Deleting audit logs...")
        await conn.execute(text("DELETE FROM audit_logs;"))
        
        print("Deleting users except Super Admins...")
        # Delete related child records for non-admin users first
        await conn.execute(text("DELETE FROM platform_identities WHERE user_id IN (SELECT id FROM users WHERE role != 'SUPER_ADMIN');"))
        await conn.execute(text("DELETE FROM user_settings WHERE user_id IN (SELECT id FROM users WHERE role != 'SUPER_ADMIN');"))
        await conn.execute(text("DELETE FROM users WHERE role != 'SUPER_ADMIN';"))

    print("✅ All data wiped successfully. Super Admins were kept.")

if __name__ == "__main__":
    asyncio.run(wipe_data())
