\set ON_ERROR_STOP on

-- Development-only reset. Keep the SUPER_ADMIN identity row(s) and static
-- configuration/content tables, while removing all khatms and user-owned data.
BEGIN;

DO $$
DECLARE
    admin_count integer;
    truncate_targets text;
BEGIN
    SELECT count(*) INTO admin_count FROM users WHERE role::text = 'SUPER_ADMIN';
    IF admin_count = 0 THEN
        RAISE EXCEPTION 'Reset aborted: no SUPER_ADMIN user exists';
    END IF;

    -- Find every table that depends (directly or transitively) on users.
    -- platform_identities is preserved long enough to retain admin login;
    -- non-admin identities are deleted below.
    WITH RECURSIVE dependent_tables(oid) AS (
        SELECT conrelid
        FROM pg_constraint
        WHERE contype = 'f' AND confrelid = 'users'::regclass
        UNION
        SELECT c.conrelid
        FROM pg_constraint c
        JOIN dependent_tables d ON c.confrelid = d.oid
        WHERE c.contype = 'f'
    )
    SELECT string_agg(format('%I.%I', n.nspname, c.relname), ', ')
    INTO truncate_targets
    FROM (
        SELECT DISTINCT oid FROM dependent_tables
    ) d
    JOIN pg_class c ON c.oid = d.oid
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relkind = 'r'
      AND c.relname NOT IN ('users', 'platform_identities');

    IF truncate_targets IS NOT NULL THEN
        EXECUTE 'TRUNCATE TABLE ' || truncate_targets || ' RESTART IDENTITY CASCADE';
    END IF;

    DELETE FROM platform_identities
    WHERE user_id NOT IN (SELECT id FROM users WHERE role::text = 'SUPER_ADMIN');

    DELETE FROM users WHERE role::text <> 'SUPER_ADMIN';
END $$;

COMMIT;

SELECT
    (SELECT count(*) FROM users) AS remaining_users,
    (SELECT count(*) FROM users WHERE role::text = 'SUPER_ADMIN') AS remaining_admins,
    (SELECT count(*) FROM khatms) AS remaining_khatms;
