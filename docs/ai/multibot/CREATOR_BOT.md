# CREATOR BOT — ختم‌ساز

The creator bot is the "main" bot. Tokens come from `.env`
(`telegram_bot_token`, `bale_bot_token`). It handles everything related to
**creating and managing** khatms, plus admin functions.

## Responsibilities

1. **Creator registration** — name, phone with OTP verification, province, city, gender
2. **Khatm creation wizard** — template picker → type (commitment/open) → settings → confirm
3. **Khatm management** — member list, stats, settings, CSV export, QR invite, broadcasts
4. **Creator request flow** — participants apply for creator access, admin approves
5. **Admin functions** — web panel, moderation, finance, system settings
6. **Wallet & payments** — top-up, plan purchase, creation fee deduction
7. **Language**: supports fa/ar/en. User picks via settings menu.

## Routers on `dp_creator`

These routers are registered ONLY on the creator Dispatcher:

| Router | File | Purpose |
|--------|------|---------|
| `start_router` | `bot/handlers/start.py` | Creator /start (no join flow) |
| `registration_router` | `bot/handlers/registration.py` | Creator registration with OTP |
| `create_khatm_router` | `bot/handlers/create_khatm.py` | Khatm creation wizard |
| `my_khatms_router` | `bot/handlers/my_khatms.py` | Creator's khatm management |
| `panel_router` | `bot/handlers/panel.py` | Inline management/admin panels |
| `admin_router` | `bot/handlers/admin.py` | Admin commands |
| `broadcast_router` | `bot/handlers/broadcast.py` | Admin broadcast moderation |
| `manage_content_router` | `bot/handlers/manage_content.py` | Content management |
| `wallet_router` | `bot/handlers/wallet.py` | Wallet operations |
| `creator_decisions_router` | `bot/handlers/creator_decisions.py` | Missed-commitment decisions |
| `creator_request_router` | `bot/handlers/creator_request.py` | Creator access requests |
| `creator_broadcast_router` | `bot/handlers/creator_broadcast.py` | Creator broadcasts to members |
| `manual_phone_verification_router` | `bot/handlers/manual_phone_verification.py` | Foreign phone verification |
| `account_link_router` | `bot/handlers/account_link.py` | Cross-platform account linking |
| `change_phone_router` | `bot/handlers/change_phone.py` | Phone change flow |

Shared routers also registered on `dp_creator`:
`help_router`, `settings_menu_router`, `timezone_settings_router`,
`font_settings_router`, `content_settings_router`, `reciter_settings_router`,
`reminder_settings_router`, `digest_settings_router`, `sms_settings_router`,
`profile_router`, `report_router`, `suggestions_router`,
`language_settings_router`.

## Creator /start behavior

When a user sends `/start` to the creator bot:

1. **First-time**: show language picker → welcome message → participant menu
2. **Returning user**: show appropriate menu based on role:
   - `SUPER_ADMIN` → admin menu
   - `CREATOR` → creator menu (Create | My Khatms | Management)
   - `USER` → participant menu (Public Khatms | Request Creator Access | Support)
3. **Deep link `join_*`**: NOT handled. Creator bot does not process invite links.
   Show a message: "این بات برای ساخت ختم است. برای شرکت در ختم، از لینک دعوت استفاده کنید."

## Creator menus (unchanged from current)

```
Creator Menu:
[ 📅 امروز ]
[ 🎛 پنل مدیریت ]
[ 💰 مالی ]
[ ⚙️ تنظیمات ] [ 📞 پشتیبانی سازنده ]

Management Panel (inline):
[ ➕ ساخت ختم جدید ] [ 📋 ختم‌های من ]
[ 📢 ارسال پیام گروهی ]
[ 🔙 بازگشت ]
```

## Post-creation: invite link generation

After a khatm is created and activated:

1. System determines `BotCategory` via `resolve_bot_category(khatm)`
2. Show language selection: "لینک دعوت برای کدام زبان‌ها ساخته شود؟"
   - [ ] فارسی
   - [ ] عربی
   - [ ] انگلیسی
3. For each selected language, look up the matching member `bot_instance`
4. Generate one shared token, build deep links for each bot
5. Show all links grouped by language, with copy buttons

See [INVITE_LINKS.md](INVITE_LINKS.md) for the full flow.
