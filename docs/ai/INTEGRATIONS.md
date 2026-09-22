# INTEGRATIONS

## Telegram

- Library: `aiogram` 3.x.
- Auth: `TELEGRAM_BOT_TOKEN` in `.env`. Get one from **@BotFather** in
  Telegram (`/newbot`).
- Transport: **long polling** (`dp.start_polling`), not a webhook — see
  DECISIONS.md DEC-PY-0001. No public URL, tunnel, or reverse proxy needed.
- `bot/telegram/client.py` builds the `Bot` instance and tags it
  `bot.khatmsaz_platform = Platform.TELEGRAM` so shared handlers know which
  platform they're replying on.
- **Local Windows dev only:** if Telegram is blocked on your network, set
  `BOT_HTTP_PROXY_URL` in `.env` to your VPN/proxy client's local HTTP proxy
  address, and see DEBUGGING.md "Bot can't reach Telegram on Windows" for
  the full story (DNS fake-IP + a Windows asyncio event-loop bug, both real,
  both worked around). Leave it empty on a real server with normal internet
  access — verified working end-to-end on 2026-09-15 with a real
  `@Khatm_Saz_bot` token from this exact laptop once both fixes were in.

## Bale

- Bale's Bot API is Telegram-Bot-API-compatible at a different base URL
  (`https://tapi.bale.ai` by default, configurable via `BALE_API_BASE_URL`).
  Reused `aiogram` with a custom `TelegramAPIServer` base instead of a
  second bot framework — see `bot/bale/client.py`.
- Auth: `BALE_BOT_TOKEN` in `.env`. Get one from **Bale's bot platform**
  (ربات‌ساز بله) — ask the user for the exact current registration URL if
  this needs re-verifying; do not guess a URL.
- Also long polling, same rationale as Telegram.
- **Known compatibility risk**: Bale's Bot API does not mirror 100% of
  Telegram's feature set (e.g. some inline keyboard or file-type behaviors
  may differ). When a handler uses a Telegram-specific feature, test it
  against Bale specifically before assuming parity — don't assume "it works
  on Telegram" implies "it works on Bale."

## Cross-platform invitation links

- After production DNS/TLS, set `PUBLIC_WEB_BASE_URL=https://khatmsaz.com`.
  New invitation messages and QR codes then use `/join/<token>`, which previews
  the khatm and offers Telegram/Bale continuation with the same `join_` payload.
- If no public origin is configured, Telegram keeps its direct deep link and
  Bale falls back to the raw `/start join_<token>` command when needed.

## Identity across platforms

See DOMAIN_MODEL.md §1 and DECISIONS.md DEC-PY-0003/DEC-PY-0061. Phone number
(verified, Creator-only for now) is the cross-platform merge key.
`/link_account` lets a user link the current Telegram/Bale account to their
existing phone-verified User via OTP. The current account must still be a
pristine provisional account; used accounts require support review rather than
an automatic data/wallet merge.

## SMS

- OTP sending is integrated behind the `SmsProvider` interface. The default
  `noop` provider deliberately refuses production delivery.
- Kavenegar is the production adapter selected by the original requirements.
  Set `SMS_PROVIDER=kavenegar`, `SMS_API_KEY`, and `SMS_SENDER`; the optional
  `SMS_API_BASE_URL` defaults to `https://api.kavenegar.com/v1`. The adapter
  calls `POST /{api-key}/sms/send.json`, converts Iranian E.164 numbers to the
  local `09...` receptor form, checks both HTTP and provider status, and never
  includes the API key in normalized errors.
- `DEV_OTP=1` displays the test code only for local development and must never
  be enabled in production.
- Live sending still needs the account's API key and approved service sender.

## Payments

- PayPing v3 is the first concrete adapter because that is the merchant
  account supplied by the project owner (DEC-PY-0056). Create uses
  `POST /v3/pay`; the documented form callback is received at
  `/payments/payping/callback`; final confirmation uses
  `POST /v3/pay/verify`. ZarinPal/Saman can remain later adapters behind the
  same gateway boundary.
- **Never trust a client-supplied user id when verifying a payment.** The
  user id is fixed at intent-creation time server-side. PayPing receives the
  local pending-payment UUID as `clientRefId`; callback fields and verified
  response are matched against that stored row, then the intent is claimed
  atomically. A browser return by itself never credits a wallet.
- Configuration names are `PAYPING_API_TOKEN` and
  `PAYPING_CALLBACK_URL`; panel credentials must never be stored in the
  project. See `docs/PAYPING-SETUP-FA.md`.

## Redis

- `REDIS_URL` reserved for: wizard/conversation state (multi-step bot
  flows) and the reminder scheduler (APScheduler jobstore). Neither is wired
  yet (Phase 1/2).

## Content storage (Quran pages, audio)

- Quran image/audio delivery now uses canonical source-message references in
  the private Telegram channel, with a versioned complete 604-page map and
  Parhizgar audio coverage. References are platform-scoped and forwarded
  once per physical source post. The bot still needs membership in that
  channel before the live forwarding check can pass. Local archive naming is
  documented in `docs/PAYPING-SETUP-FA.md`.
