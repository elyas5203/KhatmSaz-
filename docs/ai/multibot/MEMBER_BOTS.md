# MEMBER BOTS — بات‌های ختم

Each member bot serves one content category in one language. A member bot's
only job is letting users participate in khatms — it never creates or manages
khatms.

## Language isolation

A member bot's language is determined by its `bot_instances.language` value,
NOT by the user's settings. All text sent by the bot uses this fixed language.

- No language-switcher menu in member bots
- User's `UserSettings.language` is NOT used for member bot text
- The `i18n.t(key, lang=bot.khatmsaz_language)` pattern is used everywhere

When the same user is in multiple member bots (e.g., Quran-FA for one khatm
and Salawat-AR for another), they get messages in the appropriate language
from each bot.

## Routers on `dp_member`

These routers are registered ONLY on the member Dispatcher:

| Router | File | Purpose |
|--------|------|---------|
| `member_start_router` | `bot/handlers/member_start.py` | NEW — /start with join flow |
| `member_registration_router` | `bot/handlers/member_registration.py` | NEW — simplified registration |
| `member_my_khatms_router` | `bot/handlers/member_my_khatms.py` | NEW — participant-only khatm list |
| `portions_router` | `bot/handlers/portions.py` | Portion completion, contribution |
| `devotional_router` | `bot/handlers/devotional.py` | Dua/ziyarat content delivery |
| `leave_router` | `bot/handlers/leave.py` | Leave a khatm |
| `join_requests_router` | `bot/handlers/join_requests.py` | Private khatm approve/reject |
| `public_khatms_router` | `bot/handlers/public_khatms.py` | Browse public khatms |

Shared routers also registered on `dp_member`:
`help_router`, `settings_menu_router`, `timezone_settings_router`,
`font_settings_router`, `content_settings_router`, `reciter_settings_router`,
`reminder_settings_router`, `profile_router`, `report_router`,
`suggestions_router`.

**NOT on `dp_member`**: `language_settings_router` (language is fixed per bot).

## Member /start behavior

**File**: `bot/handlers/member_start.py`

### Without deep link

```
/start  (no payload)
```

1. Provision user if first-ever contact
2. Show welcome message (in bot's language):
   - Bot name + description
   - "با لینک دعوت می‌توانید در ختم شرکت کنید."
3. List public khatms of this bot's category (if any exist):
   - Filter: `khatm.visibility == PUBLIC` AND matching `BotCategory`
   - Show as inline keyboard buttons
4. Show member menu

### With invite deep link

```
/start join_{TOKEN}
```

1. Resolve token → khatm_id (same as current `start.py`)
2. Validate khatm exists, is active, not expired
3. Validate khatm's `BotCategory` matches this bot's category
   - If mismatch: "این ختم مربوط به بات دیگری است." + correct bot link
4. Platform restriction check (Telegram-only / Bale-only)
5. Show join preview → "شرکت در ختم" button
6. If user not registered → member registration flow
7. If commitment → show consent text → join
8. Record `joined_via_bot_instance_id` on participation

## Member registration

**File**: `bot/handlers/member_registration.py`

Simplified version of creator registration. 5 steps, all in the bot's
fixed language:

1. **Name** — full name (free text)
2. **Phone** — contact-share button on Telegram; manual typing on Bale.
   **No OTP verification** (trust-based, same as current participant flow)
3. **Province** — inline keyboard (31 Iran provinces + "خارج از ایران")
4. **City** — free text
5. **Gender** — Male / Female inline buttons

After completion, automatically resumes the pending join flow (if any).

## Member menu

```
Member Menu:
[ 📅 امروز ]
[ 📋 ختم‌های من ]
[ 🔍 ختم‌های عمومی ]
[ ⚙️ تنظیمات ] [ 📞 پشتیبانی ]
```

No "Create", no "Management", no "Finance". The settings menu omits
the language switcher.

## Member "My Khatms"

**File**: `bot/handlers/member_my_khatms.py`

Shows only khatms the user participates in **through this specific bot**
(filtered by `joined_via_bot_instance_id`).

For each khatm:
- Title + progress
- "➕ ثبت مشارکت" (contribute) button
- "⏸ توقف" / "▶️ ادامه" (pause/resume) button
- "🚪 خروج" (leave) button

No management actions (stats, settings, members, broadcasts).

## How a member can be in multiple bots

A single user can be in:
- Quran-FA bot for a Quran khatm (created by person A)
- Salawat-FA bot for a Salawat khatm (created by person B)
- Quran-FA bot for ANOTHER Quran khatm (created by person C)

Each bot is a separate conversation. The member menu in each bot only shows
khatms joined through that bot. Notifications for each khatm come from the
bot the member joined through.
