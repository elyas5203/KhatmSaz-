# INVITE LINKS — Multi-Bot Link Generation

## Current behavior (single bot)

All invite links point to one bot:
```
t.me/Khatm_Saz_bot?start=join_{TOKEN}
ble.ir/KhatmSazBale_bot?start=join_{TOKEN}
```

## New behavior (multi-bot)

Links now point to the correct **member bot** based on khatm category and
language:
```
t.me/KhatmQuranFA_bot?start=join_{TOKEN}      ← Quran, Farsi, Telegram
t.me/KhatmQuranAR_bot?start=join_{TOKEN}      ← Quran, Arabic, Telegram
ble.ir/KhatmQuranFA_bot?start=join_{TOKEN}     ← Quran, Farsi, Bale
```

**Key design**: all language variants share the **same token**. The token
resolves to the same khatm — only the bot (and therefore the language) differs.

## Link generation flow

### Step 1: Khatm creation completes

In `create_khatm.py`, after `workflow_service.create_and_launch_khatm()`:

1. `resolve_bot_category(khatm)` determines the category (e.g., QURAN)
2. System checks which member bots are configured for this category

### Step 2: Language selection

Creator sees a new step in the wizard:

```
لینک دعوت برای کدام زبان‌ها ساخته شود؟

[✓] فارسی
[ ] عربی
[ ] انگلیسی

[تایید]
```

Default: only the creator's own language is pre-selected.

Only languages with a configured+active member bot are shown. If a language
has no bot configured, it doesn't appear in the list.

### Step 3: Token generation

One token is generated via `invitation_service.issue_invitation()` (existing
code). The same token is used for ALL language variants.

### Step 4: Link building

For each (selected_language × active_platform):

```python
bot_instance = registry.get_member_bot(platform, category, language)
if bot_instance:
    link = f"https://t.me/{bot_instance.username}?start=join_{token}"
```

### Step 5: Display to creator

```
✅ ختم «نام ختم» با موفقیت ساخته شد!

🔗 لینک‌های دعوت:

🇮🇷 فارسی:
  تلگرام: t.me/KhatmQuranFA_bot?start=join_abc123
  بله: ble.ir/KhatmQuranFA_bot?start=join_abc123

🇸🇦 عربی:
  تلگرام: t.me/KhatmQuranAR_bot?start=join_abc123
  بله: ble.ir/KhatmQuranAR_bot?start=join_abc123
```

## Token resolution on member bot

When a user clicks a link and arrives at a member bot:

1. `/start join_{TOKEN}` → extract token
2. `invitation_service.resolve_khatm_id(token)` → khatm_id (unchanged)
3. Load khatm from DB
4. **Category validation**: check that `resolve_bot_category(khatm)` matches
   `bot.khatmsaz_category`. If mismatch → error message with correct bot link.
5. Continue with normal join flow (preview → registration → join)

## Web landing page changes

**Route**: `/join/{token}` in `web/app.py`

Currently shows two buttons: "Open in Telegram" / "Open in Bale".

New behavior:
1. Resolve token → khatm
2. Determine `BotCategory`
3. For each configured language × platform:
   - Show a button: "شرکت از تلگرام (فارسی)" etc.
4. Each button links to the correct member bot deep link

## Retrieving links later

Creator can get invite links again from the khatm management panel
(`my_khatms.py` → manage → "QR دعوت" or inline share).

The system re-fetches the active invitation token and rebuilds links using
the current `BotRegistry` state. If a new language bot was added since
creation, links for it will now appear.

## QR codes

QR codes are generated per-link. Since there are now multiple links per
khatm, the QR screen shows one QR per language/platform combo.

## Edge cases

- **No member bot configured**: if the owner hasn't set up any member bots
  yet, links fall back to the creator bot (degraded single-bot mode).
- **Bot deactivated after links were shared**: the link still works — users
  just won't get the /start response until the bot is reactivated.
- **Token shared on wrong bot**: if someone manually types the token on a
  different category bot, the category validation catches it and shows
  the correct bot to use.
