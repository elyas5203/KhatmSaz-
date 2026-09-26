# HANDLER ROUTING — Two Dispatchers

## Architecture

Instead of one `Dispatcher` for all bots, the system uses two:

| Dispatcher | Polls | Purpose |
|------------|-------|---------|
| `dp_creator` | Creator bots (2: Telegram + Bale) | Creation, management, admin |
| `dp_member` | Member bots (up to 24) | Joining, participation, portions |

Both Dispatchers run in the same process, same event loop. They share:
- The database (SQLAlchemy engine)
- The `BotRegistry` singleton
- The APScheduler instance
- The `notify_fn` callback

## Router classification

### Creator-only routers

These handle operations that only make sense on the creator bot:

```python
# bootstrap.py — registered on dp_creator only
dp_creator.include_router(start_router)           # creator /start
dp_creator.include_router(registration_router)     # OTP registration
dp_creator.include_router(create_khatm_router)     # khatm wizard
dp_creator.include_router(my_khatms_router)        # creator khatm management
dp_creator.include_router(panel_router)            # inline panels
dp_creator.include_router(admin_router)            # admin commands
dp_creator.include_router(broadcast_router)        # admin broadcasts
dp_creator.include_router(manage_content_router)   # content admin
dp_creator.include_router(wallet_router)           # payments
dp_creator.include_router(creator_decisions_router)
dp_creator.include_router(creator_request_router)
dp_creator.include_router(creator_broadcast_router)
dp_creator.include_router(manual_phone_verification_router)
dp_creator.include_router(account_link_router)
dp_creator.include_router(change_phone_router)
```

### Member-only routers

These handle operations that only make sense on member bots:

```python
# bootstrap.py — registered on dp_member only
dp_member.include_router(member_start_router)          # NEW
dp_member.include_router(member_registration_router)   # NEW
dp_member.include_router(member_my_khatms_router)      # NEW
dp_member.include_router(portions_router)              # existing, moved
dp_member.include_router(devotional_router)            # existing, moved
dp_member.include_router(leave_router)                 # existing, moved
dp_member.include_router(join_requests_router)         # existing, moved
dp_member.include_router(public_khatms_router)         # existing, moved
```

### Shared routers

These are registered on BOTH dispatchers:

```python
for dp in (dp_creator, dp_member):
    dp.include_router(help_router)
    dp.include_router(settings_menu_router)
    dp.include_router(timezone_settings_router)
    dp.include_router(font_settings_router)
    dp.include_router(content_settings_router)
    dp.include_router(reciter_settings_router)
    dp.include_router(reminder_settings_router)
    dp.include_router(digest_settings_router)
    dp.include_router(sms_settings_router)
    dp.include_router(profile_router)
    dp.include_router(report_router)
    dp.include_router(suggestions_router)
```

**Exception**: `language_settings_router` is creator-only (member bots have
fixed language).

## Middleware

`ModerationMiddleware` is registered as outer middleware on BOTH dispatchers
(unchanged from current behavior — it blocks SUSPENDED/BANNED users).

## Polling startup

```python
# bootstrap.py
polling_creator = asyncio.create_task(
    dp_creator.start_polling(*registry.creator_bots())
)
polling_member = asyncio.create_task(
    dp_member.start_polling(*registry.member_bots())
)
# + optional web server task
await asyncio.gather(polling_creator, polling_member, web_task)
```

If no member bots are configured (empty list), `dp_member.start_polling()`
is skipped entirely — the system runs in "creator-only" mode (identical to
current single-bot behavior).

## How handlers know which bot they're on

Every handler receives the `Bot` object in `data["bot"]`. To check:

```python
bot = data["bot"]
bot.khatmsaz_role       # BotRole.CREATOR or BotRole.MEMBER
bot.khatmsaz_category   # BotCategory.QURAN etc. (None for creator)
bot.khatmsaz_language   # "fa" / "ar" / "en" (None for creator)
bot.khatmsaz_instance_id  # UUID of the bot_instances row
```

In member handlers, use `bot.khatmsaz_language` instead of looking up the
user's language preference.

## Modifying existing handlers

Some existing handlers (e.g., `portions.py`) currently assume a single bot.
Changes needed:

1. **Language resolution**: use `bot.khatmsaz_language` when the handler runs
   on a member bot, fall back to `user_settings.language` on creator bot.
   Helper: `resolve_lang(bot, user_settings)` in `bot/navigation.py`.

2. **Notification sending**: when a handler needs to notify someone on a
   different bot (e.g., creator notification about a member action), use
   `registry.get_creator_bot(platform)` instead of `data["bot"]`.

3. **Menu keyboards**: use `member_menu_keyboard(lang)` on member bots,
   existing role-based keyboards on creator bot.
