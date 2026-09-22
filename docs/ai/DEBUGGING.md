# DEBUGGING

Real, recurring problems only — not a running log of every bug ever fixed
(that's CHANGELOG.md). Delete an entry only if the underlying cause is fully
gone (e.g. the library was replaced).

---

### Docker container is running but port 55433 is not published on Windows
**Symptom:** `docker exec ... pg_isready` succeeds, `HostConfig.PortBindings`
still contains `55433:5432`, but `docker ps` shows only `5432/tcp`,
`NetworkSettings.Ports` is empty, and the app gets connection refused on
localhost:55433. Recreating the container may still reproduce the problem.

**Cause observed on 2026-09-20:** Docker Desktop's Linux networking backend
failed to apply port publishing after an engine restart. This is distinct
from PostgreSQL readiness inside the container. Docker was also configured
to use a local proxy at `127.0.0.1:12334`, which prevented pulling a temporary
Python image when that proxy was unreachable from the Docker VM.

**Safe diagnosis:**
```powershell
docker exec khatmsaz-py-postgres pg_isready -U khatmsaz
docker ps --filter name=khatmsaz-py-postgres --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
docker inspect -f "{{json .HostConfig.PortBindings}} {{json .NetworkSettings.Ports}}" khatmsaz-py-postgres
Get-NetTCPConnection -LocalPort 55433 -State Listen -ErrorAction SilentlyContinue
```

Do not claim the bot is healthy merely because in-container `pg_isready`
passes. The public `/health` endpoint now verifies the app-to-database path
and returns 503 when it is broken. For the 2026-09-20 recovery, an isolated
PostgreSQL 18 cluster was created in the Windows temporary directory, the
Docker database was copied with `pg_dump -Fc`, and the copy was restored
locally. The Docker volume and backup container were retained untouched.

---

### After the dev laptop sleeps/restarts: DB container exited, bot process orphaned
**Symptom:** `alembic current` (or the bot itself) fails with a connection
error after coming back to the machine later (e.g. next day); background
bot-process task notifications show up as "stopped" with no completion
record from the previous session.
**Cause:** `khatmsaz-py-postgres` is a plain `docker run` container (no
restart policy), so it doesn't survive the host sleeping or Docker Desktop
restarting. The bot process, if it was running as a backgrounded shell
command, doesn't survive either.
**Fix — every time the dev environment comes back after being idle:**
```bash
docker start khatmsaz-py-postgres
docker exec khatmsaz-py-postgres pg_isready -U khatmsaz   # confirm before doing anything else
# then check for a live bot process before starting a new one — see the
# "two bot processes" entry below — and start it if none is running.
```
**Not a concern on the real VPS deployment**: `docs/DEPLOY-GUIDE-FA.md`'s
systemd service (`Restart=always`) and a real Postgres install/service
don't have this problem — this is purely a local-dev-on-a-laptop issue.

---

### Bot can't reach Telegram on Windows (local dev only)
**Symptom:** `python -m khatmsaz.bootstrap` raises `TelegramNetworkError` /
`ClientConnectorError: Cannot connect to host api.telegram.org` — either an
immediate "connection refused" or a long hang ending in a Windows socket
error (`WinError 121`/`WinError 1225`), even though `curl https://api.telegram.org`
from the same machine works fine.
**Cause — two separate issues that both showed up on this dev machine:**
1. **DNS fake-IP + no system-proxy awareness.** On a network where Telegram
   is blocked (this describes most ISPs in Iran) and a VPN/proxy client is
   used to reach it, that client often intercepts DNS and resolves
   `api.telegram.org` to a private "fake IP" (seen here: `10.10.34.35`) that
   is only routable through the client's own proxy port. `curl` on Windows
   automatically honors the system proxy (WinHTTP); Python's `aiohttp` does
   not — it tries to open a raw socket to the fake IP directly and gets
   refused.
   **Fix:** find the VPN/proxy client's local HTTP proxy port (check
   `netstat -an | findstr LISTENING` for a `127.0.0.1:<port>` with many
   established connections — that's almost always it) and set
   `BOT_HTTP_PROXY_URL=http://127.0.0.1:<port>` in `.env`. Requires the
   `aiohttp-socks` package (in `requirements.txt`) — aiogram's
   `AiohttpSession` raises a clear `RuntimeError` telling you to install it
   if it's missing.
2. **Windows `ProactorEventLoop` + TLS-over-proxy hangs.** Even with the
   proxy configured, connecting via an HTTP CONNECT tunnel (required for
   HTTPS through an HTTP proxy) can hang indefinitely on Windows because
   `asyncio`'s default event loop (`ProactorEventLoop`) has a known bug with
   `loop.start_tls()` on an already-connected socket.
   **Fix:** `bootstrap.py`'s `if __name__ == "__main__":` block sets
   `asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())`
   on Windows before calling `asyncio.run(main())`. This is safe to always
   do on Windows — it isn't proxy-specific, and the older selector loop
   doesn't have this bug.
**On a real Linux VPS with normal (unblocked) internet access, neither of
these applies** — leave `BOT_HTTP_PROXY_URL` empty and the Windows-only
event-loop branch never runs (checked via `sys.platform == "win32"`).

---

### Two bot processes end up polling the same token at once
**Symptom:** the *same* incoming Telegram update gets processed twice,
racing two concurrent DB writes for what should be a single insert (this is
what first exposed the two bugs below — both showed up as "duplicate key"
`IntegrityError`s from what looked like one `/start` press).
**Cause:** a previous `python -m khatmsaz.bootstrap` process didn't fully
exit (e.g. it crashed on a startup error but the OS process lingered) and a
second one was started on top of it. Long polling has no built-in guard
against two consumers of the same bot token.
**How to check:** `powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object {\$_.CommandLine -like '*khatmsaz.bootstrap*'}"`
— if this lists more than one process, kill all of them and start exactly
one.
**Prevention:** always confirm the previous instance actually exited (check
the process list, not just the terminal output) before starting a new one,
especially right after a crash.

---

### Check-then-insert races in module services (identity, participation)
**Symptom:** `sqlalchemy.exc.IntegrityError` / `UniqueViolationError` on a
partial-unique or unique index, thrown out of a service function and
crashing the handler, even though the DB constraint itself is working
correctly (it's *supposed* to reject the duplicate — the bug is that nothing
catches it).
**Cause:** several services follow a "check if a row exists, then insert if
not" pattern (`identity.resolve_or_provision_user`,
`participation.service.join`) without any locking. Two coroutines handling
two updates for the *same* logical operation (e.g. Telegram delivering
several queued `/start` presses from one chat at once, or a double-tapped
invite link) can both pass the "doesn't exist yet" check before either has
committed, so both try to insert and the loser hits the unique constraint.
**Fix (the pattern to copy for any new module with the same shape):**
1. Wrap the insert in `async with session.begin_nested():` (a SAVEPOINT) in
   `repository.py`, so a failed insert only rolls back that one operation —
   not the whole outer transaction, and doesn't leave a half-written row
   from an earlier insert in the same function (see
   `identity/repository.py::create_user_with_platform_identity`, which
   inserts a `User` *and* a `PlatformIdentity` — without the savepoint, a
   lost race on the second insert would still leave the first commit-bound
   inside the outer transaction until something else rolled it back).
2. In `service.py`, catch `sqlalchemy.exc.IntegrityError` around the create
   call and re-query for the row the winner just created, returning that
   instead of raising — the caller sees "the thing exists" either way,
   never a crash.
**Where to check next:** any future module with a similar
"look up or create" or "look up or join" shape (waiting list promotion,
wallet lazy-creation, OTP challenge creation) should get the same treatment
proactively, not just when it crashes in testing.

---

### A wizard's free-text step swallows a menu-button press
**Symptom:** while a multi-step FSM conversation (e.g. the khatm creation
wizard) is waiting for free text, pressing an unrelated reply-keyboard
button (e.g. "🕋 ختم‌های من") gets treated as the answer to the current
wizard question instead of navigating away. Concretely observed: a khatm
literally created with the title `🕋 ختم‌های من`.
**Cause:** a state-scoped text handler (`@router.message(StateFilter(...))`)
matches *any* text while that state is active, and aiogram checks routers/
handlers in registration order — the wizard's router was registered before
the menu-button router in `bootstrap.py`, so the wizard always won the race
for that message regardless of its content.
**Fix:** every free-text wizard step must call
`bot.keyboards.bail_if_menu_button(message, state)` first and `return` if it
returns `True` (it already clears the FSM state and replies) — see
`create_khatm.py`'s `enter_title`/`enter_niyyat`/`enter_target` and
`portions.py`'s `receive_contribution_amount` for the pattern. Add the same
guard to any new free-text FSM step.

### UUID primary key compared unequal to itself across a session boundary
**Symptom:** two `User` objects fetched in different `session_scope()` calls,
both printing the *same* id string, compare `False` with `==`.
**Cause:** `core/ids.py::new_id()` returned a `str`; a freshly-inserted row's
`.id` attribute kept that `str` (no refresh, since `expire_on_commit=False`),
while a row fetched via `select()` came back as a real `uuid.UUID` (the
column's mapped Python type). `"abc" == UUID("abc")` is `False` even though
both stringify identically.
**Fix:** `new_id()` returns `uuid.UUID` directly (fixed 2026-09-15, see
PROJECT_STATE.md Phase 0 entry). **When writing a new module's
`repository.py`, always assign `id=new_id()` (the UUID object), never
`id=str(new_id())` or `id=str(uuid7())`.**
**How to catch it again if it recurs:** any equality/identity check between
a just-created ORM object and one re-fetched from the DB is a good smoke
test to run once per new module — it would have caught this immediately.

---

### `alembic revision --autogenerate` needs a real Postgres, not sqlite
**Symptom:** autogenerate against sqlite either errors on `postgresql.UUID`/
`ARRAY` types or silently produces a wrong diff.
**Cause:** the schema deliberately uses Postgres-only types (ported 1:1 from
the original Prisma schema, which also targeted Postgres only).
**Fix:** always point `DATABASE_URL` at real Postgres when generating or
testing a migration. If none is installed locally, use a throwaway Docker
container — see DATABASE.md's "Verifying schema changes locally" section.
Check `docker images` first; a Postgres image may already be cached locally
(no network pull needed) even when `docker pull` would fail due to no
outbound registry access in a sandboxed environment.
