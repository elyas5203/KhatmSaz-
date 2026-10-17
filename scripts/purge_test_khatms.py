import argparse
import asyncio
import sys
from uuid import UUID

from sqlalchemy import text

from khatmsaz.core.db import session_scope

def normalize_phone(phone: str) -> str:
    cleaned = phone.strip().replace(" ", "").replace("-", "")
    if cleaned.startswith("09"):
        return "+98" + cleaned[1:]
    elif cleaned.startswith("9") and len(cleaned) == 10:
        return "+98" + cleaned
    elif cleaned.startswith("+98"):
        return cleaned
    return cleaned

async def run_purge(phones: list[str], execute: bool = False):
    norm_phones = [normalize_phone(p) for p in phones]
    print(f"[*] Normalized target phones: {norm_phones}")

    async with session_scope() as session:
        # 1. Resolve user IDs
        q_users = """
        SELECT DISTINCT u.id, u.display_name, u.role, 
               p.e164 as claim_phone, s.contact_phone
        FROM users u
        LEFT JOIN phone_claims p ON p.user_id = u.id
        LEFT JOIN user_settings s ON s.user_id = u.id
        WHERE p.e164 = ANY(:phones) OR s.contact_phone = ANY(:phones)
        """
        user_rows = (await session.execute(text(q_users), {"phones": norm_phones})).fetchall()
        if not user_rows:
            print("[!] No users found for given phone numbers.")
            return

        user_ids = list({r[0] for r in user_rows})
        print(f"[*] Found {len(user_ids)} matching test user accounts:")
        for r in user_rows:
            print(f"    - User: {r[0]} | Name: '{r[1]}' | Role: {r[2]} | Phone: {r[3] or r[4]}")

        # 2. Find khatms created by these users
        q_khatms = """
        SELECT id, title, template_type, khatm_type, status, creator_user_id
        FROM khatms
        WHERE creator_user_id = ANY(:uids)
        """
        created_khatms = (await session.execute(text(q_khatms), {"uids": user_ids})).fetchall()
        created_khatm_ids = [k[0] for k in created_khatms]
        print(f"\n[*] Found {len(created_khatms)} Khatms created by these accounts:")
        for k in created_khatms:
            print(f"    - Khatm: {k[0]} | '{k[1]}' | {k[2]}/{k[3]} | Status: {k[4]}")

        # 3. Find participations to delete:
        # a) All participations in the khatms created by these accounts (all members)
        # b) Any participations of these test users in other khatms
        q_participations = """
        SELECT p.id, p.khatm_id, p.user_id, k.title
        FROM khatm_participations p
        JOIN khatms k ON k.id = p.khatm_id
        WHERE p.khatm_id = ANY(:khatm_ids) OR p.user_id = ANY(:uids)
        """
        part_rows = (await session.execute(text(q_participations), {
            "khatm_ids": created_khatm_ids,
            "uids": user_ids
        })).fetchall()
        participation_ids = list({p[0] for p in part_rows})
        print(f"\n[*] Found {len(participation_ids)} Participations (memberships) to delete:")
        for p in part_rows:
            is_own_khatm = p[1] in created_khatm_ids
            is_own_user = p[2] in user_ids
            print(f"    - Part: {p[0]} | Khatm: '{p[3]}' | OwnKhatm={is_own_khatm} | OwnUser={is_own_user}")

        # 4. Count related records
        print("\n[*] Inspecting dependent rows:")
        
        # share_occurrences
        so_res = await session.execute(
            text("SELECT count(*) FROM share_occurrences WHERE participation_id = ANY(:pids)"),
            {"pids": participation_ids}
        )
        so_count = so_res.scalar() or 0
        
        # share_messages
        sm_res = await session.execute(
            text("""
            SELECT count(*) FROM share_messages 
            WHERE occurrence_id IN (
                SELECT id FROM share_occurrences WHERE participation_id = ANY(:pids)
            )
            """),
            {"pids": participation_ids}
        )
        sm_count = sm_res.scalar() or 0

        # open_contributions
        oc_res = await session.execute(
            text("SELECT count(*) FROM open_contributions WHERE participation_id = ANY(:pids) OR khatm_id = ANY(:kids)"),
            {"pids": participation_ids, "kids": created_khatm_ids}
        )
        oc_count = oc_res.scalar() or 0

        # open_reservations
        ores_res = await session.execute(
            text("SELECT count(*) FROM open_reservations WHERE participation_id = ANY(:pids) OR khatm_id = ANY(:kids)"),
            {"pids": participation_ids, "kids": created_khatm_ids}
        )
        ores_count = ores_res.scalar() or 0

        # committed_quantity_logs
        cql_res = await session.execute(
            text("SELECT count(*) FROM committed_quantity_logs WHERE participation_id = ANY(:pids) OR khatm_id = ANY(:kids)"),
            {"pids": participation_ids, "kids": created_khatm_ids}
        )
        cql_count = cql_res.scalar() or 0

        # commitment_deliveries
        cd_res = await session.execute(
            text("SELECT count(*) FROM commitment_deliveries WHERE participation_id = ANY(:pids)"),
            {"pids": participation_ids}
        )
        cd_count = cd_res.scalar() or 0

        # assignments
        asgn_res = await session.execute(
            text("SELECT count(*) FROM assignments WHERE participation_id = ANY(:pids) OR khatm_id = ANY(:kids)"),
            {"pids": participation_ids, "kids": created_khatm_ids}
        )
        asgn_count = asgn_res.scalar() or 0

        # notification_log
        nl_res = await session.execute(
            text("SELECT count(*) FROM notification_log WHERE participation_id = ANY(:pids)"),
            {"pids": participation_ids}
        )
        nl_count = nl_res.scalar() or 0

        # notification_preferences
        np_res = await session.execute(
            text("SELECT count(*) FROM notification_preferences WHERE participation_id = ANY(:pids)"),
            {"pids": participation_ids}
        )
        np_count = np_res.scalar() or 0

        # khatm_portions
        kp_res = await session.execute(
            text("SELECT count(*) FROM khatm_portions WHERE participation_id = ANY(:pids) OR khatm_id = ANY(:kids)"),
            {"pids": participation_ids, "kids": created_khatm_ids}
        )
        kp_count = kp_res.scalar() or 0

        # khatm_allocation_plans
        kap_res = await session.execute(
            text("SELECT count(*) FROM khatm_allocation_plans WHERE khatm_id = ANY(:kids)"),
            {"kids": created_khatm_ids}
        )
        kap_count = kap_res.scalar() or 0

        # khatm_broadcasts
        kb_res = await session.execute(
            text("SELECT count(*) FROM khatm_broadcasts WHERE khatm_id = ANY(:kids)"),
            {"kids": created_khatm_ids}
        )
        kb_count = kb_res.scalar() or 0

        # khatm_invitations
        ki_res = await session.execute(
            text("SELECT count(*) FROM khatm_invitations WHERE khatm_id = ANY(:kids)"),
            {"kids": created_khatm_ids}
        )
        ki_count = ki_res.scalar() or 0

        # khatm_reciters
        kr_res = await session.execute(
            text("SELECT count(*) FROM khatm_reciters WHERE khatm_id = ANY(:kids)"),
            {"kids": created_khatm_ids}
        )
        kr_count = kr_res.scalar() or 0

        # notification_jobs
        nj_res = await session.execute(
            text("SELECT count(*) FROM notification_jobs WHERE khatm_id = ANY(:kids)"),
            {"kids": created_khatm_ids}
        )
        nj_count = nj_res.scalar() or 0

        # waiting_list
        wl_res = await session.execute(
            text("SELECT count(*) FROM waiting_list WHERE khatm_id = ANY(:kids)"),
            {"kids": created_khatm_ids}
        )
        wl_count = wl_res.scalar() or 0

        # audit_logs
        al_res = await session.execute(
            text("SELECT count(*) FROM audit_logs WHERE target_khatm_id = ANY(:kids)"),
            {"kids": created_khatm_ids}
        )
        al_count = al_res.scalar() or 0

        print(f"    - share_messages: {sm_count}")
        print(f"    - share_occurrences: {so_count}")
        print(f"    - open_contributions: {oc_count}")
        print(f"    - open_reservations: {ores_count}")
        print(f"    - committed_quantity_logs: {cql_count}")
        print(f"    - commitment_deliveries: {cd_count}")
        print(f"    - assignments: {asgn_count}")
        print(f"    - notification_log: {nl_count}")
        print(f"    - notification_preferences: {np_count}")
        print(f"    - khatm_portions: {kp_count}")
        print(f"    - khatm_allocation_plans: {kap_count}")
        print(f"    - khatm_broadcasts: {kb_count}")
        print(f"    - khatm_invitations: {ki_count}")
        print(f"    - khatm_reciters: {kr_count}")
        print(f"    - notification_jobs: {nj_count}")
        print(f"    - waiting_list: {wl_count}")
        print(f"    - audit_logs (referencing target khatms): {al_count}")
        print(f"    - khatm_participations: {len(participation_ids)}")
        print(f"    - khatms: {len(created_khatm_ids)}")

        if not execute:
            print("\n[!] DRY RUN ONLY. No changes made to database. Pass --execute to purge.")
            return

        print("\n[+] EXECUTING PURGE IN TRANSACTION...")
        # 1. share_messages
        await session.execute(
            text("""
            DELETE FROM share_messages 
            WHERE occurrence_id IN (
                SELECT id FROM share_occurrences WHERE participation_id = ANY(:pids)
            )
            """),
            {"pids": participation_ids}
        )
        # 2. share_occurrences
        await session.execute(
            text("DELETE FROM share_occurrences WHERE participation_id = ANY(:pids)"),
            {"pids": participation_ids}
        )
        # 3. open_contributions
        await session.execute(
            text("DELETE FROM open_contributions WHERE participation_id = ANY(:pids) OR khatm_id = ANY(:kids)"),
            {"pids": participation_ids, "kids": created_khatm_ids}
        )
        # 4. open_reservations
        await session.execute(
            text("DELETE FROM open_reservations WHERE participation_id = ANY(:pids) OR khatm_id = ANY(:kids)"),
            {"pids": participation_ids, "kids": created_khatm_ids}
        )
        # 5. committed_quantity_logs
        await session.execute(
            text("DELETE FROM committed_quantity_logs WHERE participation_id = ANY(:pids) OR khatm_id = ANY(:kids)"),
            {"pids": participation_ids, "kids": created_khatm_ids}
        )
        # 6. commitment_deliveries
        await session.execute(
            text("DELETE FROM commitment_deliveries WHERE participation_id = ANY(:pids)"),
            {"pids": participation_ids}
        )
        # 7. assignments
        await session.execute(
            text("DELETE FROM assignments WHERE participation_id = ANY(:pids) OR khatm_id = ANY(:kids)"),
            {"pids": participation_ids, "kids": created_khatm_ids}
        )
        # 8. notification_log
        await session.execute(
            text("DELETE FROM notification_log WHERE participation_id = ANY(:pids)"),
            {"pids": participation_ids}
        )
        # 9. notification_preferences
        await session.execute(
            text("DELETE FROM notification_preferences WHERE participation_id = ANY(:pids)"),
            {"pids": participation_ids}
        )
        # 10. khatm_portions
        await session.execute(
            text("DELETE FROM khatm_portions WHERE participation_id = ANY(:pids) OR khatm_id = ANY(:kids)"),
            {"pids": participation_ids, "kids": created_khatm_ids}
        )
        # 11. khatm_allocation_plans
        await session.execute(
            text("DELETE FROM khatm_allocation_plans WHERE khatm_id = ANY(:kids)"),
            {"kids": created_khatm_ids}
        )
        # 12. khatm_broadcasts
        await session.execute(
            text("DELETE FROM khatm_broadcasts WHERE khatm_id = ANY(:kids)"),
            {"kids": created_khatm_ids}
        )
        # 13. khatm_invitations
        await session.execute(
            text("DELETE FROM khatm_invitations WHERE khatm_id = ANY(:kids)"),
            {"kids": created_khatm_ids}
        )
        # 14. khatm_reciters
        await session.execute(
            text("DELETE FROM khatm_reciters WHERE khatm_id = ANY(:kids)"),
            {"kids": created_khatm_ids}
        )
        # 15. notification_jobs
        await session.execute(
            text("DELETE FROM notification_jobs WHERE khatm_id = ANY(:kids)"),
            {"kids": created_khatm_ids}
        )
        # 16. waiting_list
        await session.execute(
            text("DELETE FROM waiting_list WHERE khatm_id = ANY(:kids)"),
            {"kids": created_khatm_ids}
        )
        # 17. audit_logs (nullify target_khatm_id or delete)
        await session.execute(
            text("UPDATE audit_logs SET target_khatm_id = NULL WHERE target_khatm_id = ANY(:kids)"),
            {"kids": created_khatm_ids}
        )
        # 18. khatm_participations
        await session.execute(
            text("DELETE FROM khatm_participations WHERE id = ANY(:pids)"),
            {"pids": participation_ids}
        )
        # 19. khatms
        await session.execute(
            text("DELETE FROM khatms WHERE id = ANY(:kids)"),
            {"kids": created_khatm_ids}
        )

        await session.commit()
        print("[✓] PURGE COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Purge test khatms and participations for given phone numbers")
    parser.add_argument("--phones", nargs="+", required=True, help="Phone numbers to purge for")
    parser.add_argument("--execute", action="store_true", help="Actually execute the deletion (irreversible)")
    args = parser.parse_args()

    asyncio.run(run_purge(args.phones, execute=args.execute))
