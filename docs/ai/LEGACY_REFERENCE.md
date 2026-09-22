# LEGACY_REFERENCE

The original TypeScript/NestJS implementation still exists, untouched, at:

```
\\wsl.localhost\Ubuntu-24.04\home\elyas\KhatmSaz
```

Do not delete it, and do not port its code directly (different language,
different architecture) — but it is the single best source of truth for
**how a domain rule was actually worked out** across 10 sprints, because it
has 397+ passing tests proving the rule was implemented correctly, and its
own `docs/ai/` memory files explain *why* each decision was made.

## What to check there, and when

| If you're building... | Read this file in the legacy repo |
|---|---|
| Any domain rule (khatm lifecycle, commitment, allocation) | `docs/ai/DOMAIN_MODEL.md`, `docs/ai/DECISIONS.md` |
| A DB schema question | `apps/api/prisma/schema.prisma` (this is what `docs/ai/DATABASE.md` here was ported from) |
| The allocation/assignment engine | `apps/api/src/allocation/**`, `apps/api/src/khatm-workflow/**` |
| Waiting list logic | `apps/api/src/waiting-list/**` |
| Notification/reminder logic | `apps/api/src/notification/**` |
| Wallet / payment / IDOR-replay fix | `apps/api/src/payment/**` (`PendingPayment` pattern) |
| Telegram/Bale bot conversation flows | `apps/api/src/telegram/**`, `apps/api/src/bale/**`, `apps/api/src/bot-shared/**` |
| Full sprint-by-sprint history of what was built and why | `docs/ai/PROJECT_STATE.md` (very long — grep for a keyword rather than reading top to bottom) |

## Known bug in the legacy deployment (context, not something to fix there)

The legacy project was deployed to a VPS with Docker; Postgres, Redis, and
the API were healthy; the Telegram webhook was receiving updates correctly
(`getMe`, webhook registration, inbound POST all verified working) — but
outbound `sendMessage` calls from `TelegramSender` were failing with a
generic network error, never fully diagnosed. This is the concrete reason
DEC-PY-0000/DEC-PY-0001 chose a from-scratch Python rewrite with long
polling instead of continuing to debug that webhook path. See the legacy
repo's own `docs/ai/PROJECT_STATE.md` (search "sendMessage") for the full
diagnostic trail if it's ever useful (e.g. to understand a Docker/ARM64/
outbound-HTTPS quirk that could resurface here too).

## Rule of thumb

If a requirement is ambiguous here and the legacy project already answered
it (and shipped it, tests passing), treat that as strong precedent — but
still confirm with the user before diverging from what's written in this
project's own `DOMAIN_MODEL.md`, since the user may have changed their mind
during the Python rewrite's requirements conversation.
