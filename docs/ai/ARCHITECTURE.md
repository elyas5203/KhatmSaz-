# ARCHITECTURE

## Shape

A single Python process (`khatmsaz.bootstrap:main`) runs one aiogram
`Dispatcher` shared by two `Bot` instances — one for Telegram, one for Bale.
Both platforms hit the same `Router`/handlers; the only platform-specific
code is the two `Bot` factories (`bot/telegram/client.py`,
`bot/bale/client.py`), which differ only in API base URL and token. A handler
that needs to know which platform it's on reads `message.bot.khatmsaz_platform`.

```
                ┌──────────────┐       ┌──────────────┐
                │   Telegram   │       │     Bale      │
                └──────┬───────┘       └──────┬────────┘
                       │  (long polling, both) │
                       ▼                       ▼
                ┌─────────────────────────────────────┐
                │        aiogram Dispatcher            │
                │  (one Router tree, shared handlers)  │
                └──────────────────┬────────────────────┘
                                   ▼
                ┌─────────────────────────────────────┐
                │     modules/<name>/service.py        │
                │   (pure business logic, no bot API)  │
                └──────────────────┬────────────────────┘
                                   ▼
                ┌─────────────────────────────────────┐
                │   modules/<name>/repository.py       │
                │      (SQLAlchemy queries only)       │
                └──────────────────┬────────────────────┘
                                   ▼
                                PostgreSQL
```

## Module isolation rule

Every domain concept is its own folder under `src/khatmsaz/modules/`:

```
modules/<name>/
  __init__.py
  models.py       # SQLAlchemy ORM models + enums for this concept
  repository.py    # SQL queries — the ONLY place session.execute() happens
  service.py        # business rules, orchestration — no SQL, no bot API calls
```

Rules that keep modules independently stable:

- **`models.py` may import another module's models only via string relationship
  names or a bare FK column** (e.g. `ForeignKey("users.id")`) — never
  `from khatmsaz.modules.khatm.models import Khatm` inside another module's
  `models.py`. This is why relationships in this codebase are mostly
  expressed as plain FK + query joins in `repository.py`, not ORM
  `relationship()` back-refs across modules — it avoids import cycles and
  means one module's file can be read/changed without pulling in the whole
  graph.
- **`service.py` never touches SQLAlchemy directly.** It calls its own
  module's `repository.py`, and when it needs another module's data, it calls
  that module's `service.py` — never that module's `repository.py` directly.
- **`bot/handlers/*.py` never contains business logic.** A handler parses the
  incoming message/callback, calls exactly one service function, and formats
  the Persian reply. If a handler function is doing `if`/`else` about domain
  rules (e.g. "is this khatm full"), that logic belongs in `service.py`.
- **A module that is "done" should not need to change when a new module is
  added.** If adding waiting-list logic requires editing `khatm/service.py`,
  that's a sign the two are coupled somewhere they shouldn't be — mention it
  in `DECISIONS.md` if the coupling is deliberate and unavoidable (e.g. Khatm
  and Participation genuinely share a lifecycle).

## Current module list

| Module | Tables | Status |
|---|---|---|
| `identity` | `users`, `platform_identities` | service done: provision/resolve, moderation (warn/suspend/ban/reactivate), super-admin bootstrap (DEC-PY-0013) |
| `phone` | `phone_claims`, `otp_challenges` | HMAC OTP, E.164 ownership, `/link_account`, atomic `/change_phone`, and a fail-closed creator-verification gate for create/copy with confirmation-time recheck; history preservation, takeover rejection, per-number transaction locking, and masked audit events are covered; live delivery remains SMS-provider-dependent |
| `manual_phone_verification` | `manual_phone_verifications` | non-Iranian creator/change requests, persistent review queue, Super Admin/Support review in bot and mobile web app, atomic promotion to the normal verified phone claim, audit and cross-platform result notification |
| `khatm` | `khatms` | service done: create/activate/list, public visibility, cosmetic edits, scheduled `start_at`/`end_at`, completion, and creator pause policy |
| `participation` | `khatm_participations`, `assignments` | service done (join/leave, pause/resume, Backup Reader opt-in, creator-resolution state) |
| `allocation` | `khatm_allocation_plans`, `khatm_portions` | service done for POSITIONAL (Quran pages), fixed-quantity COMMITMENT portions (Salawat), chunked progress logging, and expiring emergency claims |
| `open_contribution` | `open_contributions` | service done (free-form logging + overflow split) |
| `invitation` | `khatm_invitations` | service done (issue/resolve token) |
| `khatm_workflow` | *(none — orchestration only)* | service done: create+launch, copy, join-via-token (+ PRIVATE-khatm approval path), leave (+ committed-leave approval path), missed-commitment resolution, skip-today, pause/resume |
| `notification` | `notification_jobs`, `notification_preferences`, `notification_log` | dedup/log service done (`already_sent_today`/`record_sent`/`total_miss_count`); no scheduling of its own — `reminder_engine` drives it |
| `reminder_engine` | *(none — orchestration only)* | service done: morning reminder + deadline-miss detection for QURAN_PAGE+COMMITMENT only (DEC-PY-0008) |
| `message_template` | `message_templates` | versioned locale-keyed lookup and safe `{{placeholder}}` rendering; admin editor pending |
| `waiting_list` | `waiting_list` | service done: FIFO join/promote, scoped to QURAN_PAGE+COMMITMENT capacity overflow (DEC-PY-0010) |
| `wallet` | `wallets`, `wallet_transactions`, `pending_payments`, `wallet_invoices`, `discount_coupons`, `coupon_redemptions` | credit-first spend, ledger, immutable purchase invoices with paid/refunded lifecycle, transactional coupon limits/redemptions, gateway-neutral intents, and PayPing v3 verified callback/replay protection; live token/HTTPS deployment pending |
| `audit_log` | `audit_logs` | append-only privileged-action trail for moderation, finance, roles, content and request decisions; read-only web timeline at `/audit` |
| `completion` | *(orchestration only; timestamps live on `khatms`)* | delayed, creator-controlled, idempotent positive completion summaries across Telegram/Bale |
| `monthly_report` | *(orchestration only; dedup period on `user_settings`)* | timezone-aware previous-month positive reports with catch-up and fa/ar/en delivery |
| `plan` | `user_plans` | service done: lazy FREE default, `set_plan` |
| `settings` | `user_settings` | service done: `get_or_create`, `is_registered`, `save_profile`, and validated per-user IANA timezone — DEC-PY-0015 / SPEC Q85 |
| `session` | `sessions` | opaque, hashed, expiring purpose-scoped ADMIN/CREATOR sessions; separate cookies and route authorization, revoked on logout |
| `authorization` | `user_capabilities`, `admin_role_grants` | creator capability records plus revocable delegated admin roles and shared bot/web least-privilege permission policy |
| `account_merge` | `account_merges` | models only |
| `khatm_request` | `khatm_requests` | service done: submit/list-pending/approve/reject. Approval does NOT auto-activate the type in the wizard (DEC-PY-0014) — that needs a template registry refactor, not built |
| `broadcast` | `khatm_broadcasts` | service done: creator submission, Super Admin moderation, and one approved delivery path to active member identities |

`core/model_registry.py` imports every module's `models.py` for side effects
(so `Base.metadata` and Alembic autogenerate see the whole schema). Add a new
module's `models.py` there the moment it exists, even before it has a
`service.py`.

## Bot layer

- `bot/telegram/client.py`, `bot/bale/client.py` — `Bot` factories.
- `bot/handlers/*.py` — one file per user-facing flow (e.g. `start.py`).
  Import the module's `service.py`, never `repository.py` or `models.py`
  directly (except for enum values needed to build keyboards/labels).
- `bot/notify_adapter.py` — the *only* place a scheduled job (not a live
  update) touches a `Bot` instance. `reminder_engine.service` never imports
  aiogram; it calls a plain `notify(platform_value, chat_id, text)` callback
  that this file builds from the running `Bot` instances.
- `bot/middlewares.py::ModerationMiddleware` — outer middleware on both
  `dp.message`/`dp.callback_query`; blocks SUSPENDED/BANNED users before any
  router/state runs (DEC-PY-0013).
- `bootstrap.py` — process entrypoint; wires routers into the `Dispatcher`,
  starts polling, and starts an `AsyncIOScheduler` job that periodically
  calls `reminder_engine.run_once()` in its own `session_scope()`.

## Why long polling, not a webhook

See `DECISIONS.md` DEC-PY-0001. Short version: no public domain, reverse
proxy, or tunnel needed — removes the exact class of problem the original
deployment got stuck on.
