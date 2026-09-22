# ختم‌ساز (KhatmSaz) — Python

A Persian-first, multi-platform (Telegram + Bale) bot for organizing group
Khatms. Python rewrite of an earlier TypeScript project — see
`docs/ai/LEGACY_REFERENCE.md` for why and where that project lives.

**Start here:** [`CLAUDE.md`](CLAUDE.md) and [`docs/ai/PROJECT_STATE.md`](docs/ai/PROJECT_STATE.md)
explain the current state and how this project's memory system works — read
them before making any change, whether you're a human or an AI coding agent.

## Quick local setup

```bash
python -m venv .venv
./.venv/Scripts/pip install -r requirements.txt   # Windows
# .venv/bin/pip install -r requirements.txt        # Linux/macOS

cp .env.example .env
# fill in DATABASE_URL, TELEGRAM_BOT_TOKEN, BALE_BOT_TOKEN, OTP_HMAC_SECRET

PYTHONPATH=src ./.venv/Scripts/python -m alembic upgrade head
PYTHONPATH=src ./.venv/Scripts/python -m khatmsaz.bootstrap
```

On this Windows development machine, the simplest supported start command is:

```powershell
.\start_bot.ps1
```

It verifies that PostgreSQL is genuinely reachable on port 55433, attempts
the known local database recovery paths, applies pending Alembic migrations,
and only then starts the bot. Keep that PowerShell window open. You can also
double-click `start_bot.bat`.

## Deploying to a real server

See [`docs/DEPLOY-GUIDE-FA.md`](docs/DEPLOY-GUIDE-FA.md) — a step-by-step
guide in Persian written for zero prior programming experience.

## Mobile admin dashboard

The FastAPI dashboard starts beside the bot when `ADMIN_WEB_ENABLED=true`.
For local phone testing and the secure bot-issued login flow, see
[`docs/ADMIN-WEB-FA.md`](docs/ADMIN-WEB-FA.md).

## PayPing wallet top-up

The PayPing v3 adapter, verified callback, replay protection, and `/wallet`
and `/topup` bot flows are implemented. Token placement and live-activation
steps are documented in [`docs/PAYPING-SETUP-FA.md`](docs/PAYPING-SETUP-FA.md).

## Project layout

See [`docs/ai/ARCHITECTURE.md`](docs/ai/ARCHITECTURE.md).
