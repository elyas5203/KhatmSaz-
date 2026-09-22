# DATABASE

PostgreSQL, SQLAlchemy 2.0 async ORM (`asyncpg` driver), Alembic migrations.
The schema is a 1:1 port of the original Prisma schema
(`\\wsl.localhost\Ubuntu-24.04\home\elyas\KhatmSaz\apps\api\prisma\schema.prisma`)
— same table names, same columns (snake_case, matching Prisma's `@map`), same
enums, same invariants. If you need to know *why* a field or constraint
exists, that file's doc-comments are the original design rationale and are
still accurate; only the implementation language changed.

## Primary keys

Every table uses an app-generated **UUIDv7** primary key (`core/ids.py:
new_id()`), not a DB-generated UUIDv4 or serial. UUIDv7 is time-ordered, so
indexes don't fragment the way random UUIDs do. `new_id()` returns a
`uuid.UUID` object — **never call `str()` on it before assigning to a
`Mapped[uuid.UUID]` column**; see PROJECT_STATE.md's Phase 0 entry for the
bug this caused once already.

## Invariants SQLAlchemy can't express declaratively

Eight partial unique indexes are hand-written as raw SQL in migrations (not
derivable from `models.py` — if you regenerate a migration with
`--autogenerate` and it tries to drop these, that's a false positive; keep
them):

1. `khatm_participations`: at most one `ACTIVE` participation per (khatm, user).
2. `user_capabilities`: at most one active (non-revoked) grant per (user, type).
3. `khatm_portions`: no two `POSITIONAL` portions with the same `unit_start`
   within a plan (non-overlap).
4. `phone_claims`: at most one `VERIFIED` claim per canonical `e164`, globally.
5. `phone_claims`: at most one active (non-`REVOKED`) claim per (user, e164).
6. `phone_claims`: at most one `VERIFIED` claim per user, across all numbers.
7. `manual_phone_verifications`: at most one `PENDING` request per user.
8. `manual_phone_verifications`: at most one `PENDING` request per E.164
   number. Both are added by migration `q7r8s9t0`.

## Migration workflow

```bash
# 1. Change models.py in the relevant module.
# 2. Make sure core/model_registry.py imports that module (it should already).
# 3. Point DATABASE_URL at a real (or throwaway Docker) Postgres — never sqlite,
#    the schema uses Postgres-only types (UUID, ARRAY).
# 4. Generate:
PYTHONPATH=src python -m alembic revision --autogenerate -m "short description"
# 5. READ the generated file. Alembic misses partial indexes, CHECK constraints,
#    and sometimes enum value additions — add those by hand (see existing
#    migrations for the raw-SQL pattern).
# 6. Apply and verify:
PYTHONPATH=src python -m alembic upgrade head
# 7. If you're not sure the migration is reversible, also test:
PYTHONPATH=src python -m alembic downgrade -1 && python -m alembic upgrade head
```

Never run `Base.metadata.create_all()` against a real database — that's the
Python equivalent of Prisma `db push` and the original project explicitly
banned it as a shared-environment strategy. Migrations only.

## Adding a new column with a brand-new enum type

`op.add_column(..., sa.Enum('A', 'B', name='newenum'))` in a *hand-edited*
migration (after stripping the false-positive index drops per above) fails
with `UndefinedObjectError: type "newenum" does not exist` — the enum type
itself isn't created automatically the way autogenerate's raw output
implies. Add an explicit `op.execute("CREATE TYPE newenum AS ENUM ('A', 'B')")`
*before* the `add_column`, and pass `create_type=False` to the `sa.Enum(...)`
in that column so it doesn't try (and fail) to create it a second time. See
`migrations/versions/cf308fcab881_add_khatm_visibility.py` for the pattern.
Only matters for a genuinely new enum — adding a column that reuses an
*existing* enum type doesn't need this.

## Enum handling

Python enums (`str, enum.Enum` subclasses) map to native PostgreSQL `ENUM`
types via SQLAlchemy's automatic enum handling — same approach as Prisma's
`enum` blocks. Adding a new enum *value* later requires
`ALTER TYPE ... ADD VALUE` in a hand-written migration (SQLAlchemy/Alembic
autogenerate does not detect enum value changes reliably) — see how the
original project's `20260914000000_remove_quran_full_juz` migration handled
removing enum values, if that situation comes up again.

## Verifying schema changes locally without installing Postgres

If Postgres isn't installed on the machine, a throwaway Docker container is
the fastest way to verify a migration actually applies (not just that Python
imports without error):

```bash
docker run -d --name khatmsaz-pg-tmp -e POSTGRES_USER=khatmsaz \
  -e POSTGRES_PASSWORD=khatmsaz -e POSTGRES_DB=khatmsaz \
  -p 55432:5432 postgres:17-alpine
export DATABASE_URL="postgresql+asyncpg://khatmsaz:khatmsaz@localhost:55432/khatmsaz"
PYTHONPATH=src python -m alembic upgrade head
# ... test, then:
docker rm -f khatmsaz-pg-tmp
```
