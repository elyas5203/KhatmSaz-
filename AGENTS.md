# KhatmSaz (Python) — instructions for Codex

KhatmSaz (ختم‌ساز) is a Persian-first multi-platform (Telegram + Bale) bot for
organizing group Khatms (collective recitation of Quran, Salawat, Dua,
Ziyarat, etc). This is a **from-scratch Python rewrite** of an earlier
TypeScript/NestJS project. The old project (`docs/ai/LEGACY_REFERENCE.md`
explains where it lives and how to use it) has the exact domain rules already
worked out over 10 sprints — treat it as a **reference for behavior**, not as
code to port line-by-line.

Stack: Python 3.13, aiogram 3 (both Telegram and Bale — Bale's Bot API is
Telegram-compatible, just a different base URL), SQLAlchemy 2.0 async +
asyncpg, Alembic, PostgreSQL, Redis. Long polling, not webhooks (see
DEC-PY-0001 in DECISIONS.md) — no public domain/tunnel/reverse proxy needed.

## Start every task like this

1. **Understand the task before editing anything.** Ask if the request is ambiguous.
2. **Read `docs/ai/PROJECT_STATE.md` first.** It is the fastest orientation file
   and its newest entry is always at the top.
3. **Read `docs/ai/AI_HANDOFF_PROTOCOL.md`.** This project is worked on by
   multiple AI assistants (Codex, Codex, Antigravity) across sessions —
   that file is the shared convention for how each one signs its changes so
   the others don't get lost or redo work. Follow it every session.
4. **Check `docs/ai/BACKLOG.md`** for owner-requested work that hasn't been
   built yet, before assuming a feature doesn't exist or needs re-discussing.
   **Check `docs/ai/INDEX.md`** when you need the exact file/line for a
   specific topic (Quran, plans, waiting list, ...) instead of reading a
   whole history file.
5. **Read only the additional docs your task needs** — not all of them:
   - module layout / how things connect → `docs/ai/ARCHITECTURE.md`
   - domain concepts (Khatm, Participation, Allocation, Waiting List...) → `docs/ai/DOMAIN_MODEL.md`
   - schema / migrations → `docs/ai/DATABASE.md`
   - Telegram / Bale / SMS / payments → `docs/ai/INTEGRATIONS.md`
   - why something is the way it is → `docs/ai/DECISIONS.md`
   - what is planned / current phase → `docs/ai/ROADMAP.md`
   - a recurring bug → `docs/ai/DEBUGGING.md`
   - how the original TS project encoded a rule → `docs/ai/LEGACY_REFERENCE.md`

## Hard rules

- **Isolate modules.** Each domain concept lives in its own folder under
  `src/khatmsaz/modules/<name>/` (models.py, repository.py, service.py). A
  finished, tested module should not need to change when an unrelated module
  is added — see `docs/ai/ARCHITECTURE.md`.
- **No business rule may be invented.** If a rule is not written down in
  `docs/ai/DOMAIN_MODEL.md` or was not explicitly stated by the user, ask —
  do not guess pricing, limits, flows, wording, or entitlements. When in
  doubt, check `docs/ai/LEGACY_REFERENCE.md` for how the original project
  handled it, then confirm with the user before diverging.
- **Never expose secrets.** No tokens, keys or credentials in code, logs,
  error messages, tests, fixtures, or documentation. `.env` is never committed.
- **Migrations are reviewed, never `--autogenerate` blindly applied.** Always
  read the generated migration before running it; partial/CHECK constraints
  that SQLAlchemy can't express are hand-written (see existing migrations for
  the pattern).
- **Never deploy to production** or run destructive commands against data you
  did not create, without the user confirming first.
- **UI/UX text (bot replies) must be simple, warm, plain Persian.** No
  technical jargon, no long menus. See `docs/ai/DOMAIN_MODEL.md` § copy rules.

## Validation before you say "done"

```bash
# from the project root, with .venv active
python -m pytest
python -m alembic upgrade head   # against a real/throwaway Postgres — never sqlite
python -m mypy src               # if/when mypy is added — check ROADMAP.md
```

If a check fails and the fix is outside your task's scope, say so plainly
rather than working around it.

## After a meaningful change

Update the project memory in the same task:

- `docs/ai/PROJECT_STATE.md` — add a new dated entry **at the top**
- `docs/ai/CHANGELOG.md` — add a dated entry at the top
- `docs/ai/DECISIONS.md` — add a decision if you made one (never overwrite an
  old decision; mark it superseded and link the replacement)
- `docs/ai/ROADMAP.md` — mark items completed, never delete history
- `docs/ai/DEBUGGING.md` — only for real, recurring problems

History is preserved. Do not compact these files by deleting the past.

## End-of-task report (always produce this)

```
KHATMSAZ (PY) TASK REPORT
Task            — what was asked
Status          — PASS / PARTIAL / BLOCKED
What I Changed  — concise
Files Changed   — grouped by module
Commands Run    — command and result
Validation      — tests / migration apply / import smoke-test, each PASS / FAIL / NOT RUN + reason
Docs Updated    — which docs/ai files
Decisions Added — decision IDs
Next Step       — one short recommendation
```

Do not hide failures. Do not claim work you did not perform.
