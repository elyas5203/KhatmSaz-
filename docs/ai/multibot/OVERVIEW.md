# MULTI-BOT ARCHITECTURE — OVERVIEW

> **Read this file first** when working on anything related to the multi-bot
> split. It gives you the full picture in one page.

## Why multi-bot?

The original KhatmSaz was a single bot handling everything: creating khatms,
joining, participating, managing, admin. This caused:

- **UX confusion**: participants saw creator/admin menus they couldn't use
- **Language mixing**: all 3 languages served by one bot, no per-language isolation
- **No content separation**: a Quran participant had to scroll past Salawat khatms

The solution: split into **1 creator bot + 12 member bots**, each with a
focused responsibility and a single language.

## The 26-bot grid

| # | Platform | Role | Category | Language | Display Name |
|---|----------|------|----------|----------|-------------|
| 1 | Telegram | CREATOR | — | all | ختم‌ساز (تلگرام) |
| 2 | Bale | CREATOR | — | all | ختم‌ساز (بله) |
| 3 | Telegram | MEMBER | QURAN | fa | ختم قرآن فارسی (تلگرام) |
| 4 | Telegram | MEMBER | QURAN | ar | ختم القرآن العربي (تلگرام) |
| 5 | Telegram | MEMBER | QURAN | en | Quran Khatm (Telegram) |
| 6 | Telegram | MEMBER | SALAWAT | fa | ختم صلوات فارسی (تلگرام) |
| 7 | Telegram | MEMBER | SALAWAT | ar | ختم الصلوات العربي (تلگرام) |
| 8 | Telegram | MEMBER | SALAWAT | en | Salawat Khatm (Telegram) |
| 9 | Telegram | MEMBER | DUA_ZIYARAT | fa | ختم دعا و زیارت فارسی (تلگرام) |
| 10 | Telegram | MEMBER | DUA_ZIYARAT | ar | ختم الدعاء والزيارة العربي (تلگرام) |
| 11 | Telegram | MEMBER | DUA_ZIYARAT | en | Dua & Ziyarat Khatm (Telegram) |
| 12 | Telegram | MEMBER | LAAN | fa | ختم لعن فارسی (تلگرام) |
| 13 | Telegram | MEMBER | LAAN | ar | ختم اللعن العربي (تلگرام) |
| 14 | Telegram | MEMBER | LAAN | en | La'n Khatm (Telegram) |
| 15–26 | Bale | (same 12 as above) | | | ... (بله) |

**Total: 26 bot tokens** (13 Telegram + 13 Bale).

## Responsibilities

### Creator bot (ختم‌ساز)

- Khatm creation wizard (all types)
- Khatm management (members, stats, settings, broadcasts)
- Creator registration (with OTP phone verification)
- Admin panel (Super Admin web panel, system settings)
- Finance (wallet, plans, payments)
- Supports all 3 languages internally (user picks via settings)
- **Does NOT handle**: joining khatms, participating, portions

### Member bots (ختم قرآن / صلوات / دعا و زیارت / لعن)

- Joining khatms via invite links
- Member registration (contact-share phone, no OTP)
- Daily portions, reminders, completion tracking
- Open contribution logging
- Public khatm browsing (only khatms of this bot's category)
- **Fixed language**: determined by the bot, not the user
- **Does NOT handle**: creating khatms, management, admin, finance

## Architecture shape

```
                     One Python process
                     One PostgreSQL database
                     One event loop
                            │
              ┌─────────────┼─────────────┐
              │                           │
        dp_creator                  dp_member
      (Dispatcher)               (Dispatcher)
              │                           │
    ┌─────────┴─────────┐    ┌────────────┴────────────┐
    │  Telegram Creator  │    │  12 Telegram Member bots │
    │  Bale Creator      │    │  12 Bale Member bots     │
    └────────────────────┘    └──────────────────────────┘
              │                           │
              └─────────┬─────────────────┘
                        │
                   BotRegistry
               (singleton, in-memory)
                        │
                   bot_instances
                 (PostgreSQL table)
```

Two `Dispatcher` instances:
- `dp_creator` — creator-only routers, polls creator bots
- `dp_member` — member-only routers, polls member bots
- Shared routers (help, settings, profile) registered on both

All 26 bots share one DB, one scheduler, one `BotRegistry`.

## How invite links work

1. Creator creates a khatm in the creator bot (e.g., Quran commitment)
2. System maps the khatm's template_type → `BotCategory.QURAN`
3. Creator chooses which languages to generate links for (e.g., fa + ar)
4. System generates one shared token (reusable group link)
5. For each (language × platform), builds a deep link to the correct member bot:
   - `t.me/KhatmQuranFA_bot?start=join_{TOKEN}`
   - `t.me/KhatmQuranAR_bot?start=join_{TOKEN}`
   - `ble.ir/KhatmQuranFA_bot?start=join_{TOKEN}`
   - `ble.ir/KhatmQuranAR_bot?start=join_{TOKEN}`
6. All links resolve the same token → same khatm
7. Member joins through the FA bot → gets all notifications in Farsi from the FA bot

## Category mapping

How a Khatm is mapped to a BotCategory:

| Khatm template_type | category_group | → BotCategory |
|---------------------|----------------|---------------|
| QURAN_PAGE | — | QURAN |
| QURAN_SURAH | — | QURAN |
| SURAH | — | QURAN |
| SALAWAT | SALAWAT | SALAWAT |
| SALAWAT | LAAN | LAAN |
| DUA | DUA | DUA_ZIYARAT |
| ZIYARAT | DUA | DUA_ZIYARAT |
| CUSTOM | any | DUA_ZIYARAT (default) |

Implemented in `bot_registry/service.py::resolve_bot_category(khatm)`.

## Key files

| Purpose | Path |
|---------|------|
| Bot instance model | `src/khatmsaz/modules/bot_registry/models.py` |
| Bot registry class | `src/khatmsaz/core/bot_registry.py` |
| Bootstrap (startup) | `src/khatmsaz/bootstrap.py` |
| Creator handlers | `src/khatmsaz/bot/handlers/` (existing files) |
| Member handlers | `src/khatmsaz/bot/handlers/member_*.py` |
| Notify adapter | `src/khatmsaz/bot/notify_adapter.py` |
| Admin token panel | `src/khatmsaz/web/app.py` (route `/bots`) |
| Token template | `src/khatmsaz/web/templates/bot_tokens.html` |

## Related docs

- [BOT_REGISTRY.md](BOT_REGISTRY.md) — database table, encryption, startup loading
- [CREATOR_BOT.md](CREATOR_BOT.md) — creator bot handlers and flows
- [MEMBER_BOTS.md](MEMBER_BOTS.md) — member bot handlers, language isolation
- [INVITE_LINKS.md](INVITE_LINKS.md) — link generation and resolution
- [HANDLER_ROUTING.md](HANDLER_ROUTING.md) — two Dispatchers, router classification
- [REGISTRATION.md](REGISTRATION.md) — creator OTP vs member contact-share
- [ADMIN_TOKEN_PANEL.md](ADMIN_TOKEN_PANEL.md) — admin UI for managing bot tokens
- [NOTIFICATION_ROUTING.md](NOTIFICATION_ROUTING.md) — sending via the correct bot
