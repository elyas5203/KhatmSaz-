# ADMIN TOKEN PANEL — Managing Bot Tokens

## Overview

The admin web panel at `/bots` lets a Super Admin view and manage all 26 bot
tokens. This is where the owner enters the BotFather tokens for each member
bot.

## Access

- **Route**: `GET /bots`, `POST /bots/{id}/token`
- **Permission**: `OPERATIONS_VIEW` (or new `BOT_MANAGE` if added)
- **Template**: `bot_tokens.html`

## UI layout

### Platform tabs

Two tabs at the top: **تلگرام** | **بله**

Each tab shows a grid of 13 bot cards (1 creator + 12 member).

### Bot card

Each card shows:

```
┌──────────────────────────────────┐
│ ختم قرآن فارسی                  │
│ Category: QURAN  Lang: fa        │
│                                  │
│ Status: ● فعال / ○ غیرفعال / ⚪ تنظیم‌نشده │
│ Username: @KhatmQuranFA_bot      │
│                                  │
│ [ ✏️ ویرایش توکن ]              │
└──────────────────────────────────┘
```

Status colors:
- 🟢 **فعال**: token configured + `is_active = True`
- 🔴 **غیرفعال**: token configured + `is_active = False`
- ⚪ **تنظیم‌نشده**: `token_encrypted` is empty

### Creator bot card (special)

Creator bot cards show the token source as "از `.env`" and the edit button
is disabled — creator tokens are managed via environment variables, not the
web panel.

## Token edit flow (2-step confirmation)

### Step 1: Edit modal

Clicking "ویرایش توکن" opens a modal:

```
┌─────────────────────────────────────────┐
│ ویرایش توکن: ختم قرآن فارسی            │
│                                         │
│ توکن بات:                               │
│ [________________________________]      │
│                                         │
│ نام کاربری بات (بدون @):                │
│ [________________________________]      │
│                                         │
│ [ فعال ✓ ]                              │
│                                         │
│ [ ذخیره ]  [ انصراف ]                   │
└─────────────────────────────────────────┘
```

### Step 2: Confirmation

After clicking "ذخیره", a confirmation dialog appears:

```
┌─────────────────────────────────────────┐
│ ⚠️ تایید تغییر توکن                    │
│                                         │
│ برای تایید، نام نمایشی بات را تایپ کنید: │
│ [________________________________]      │
│                                         │
│ (باید دقیقا بنویسید: ختم قرآن فارسی)    │
│                                         │
│ [ تایید ]  [ انصراف ]                   │
└─────────────────────────────────────────┘
```

The admin must type the exact `display_name` of the bot. This prevents
accidental token changes (e.g., pasting the wrong token into the wrong bot).

### Step 3: Save

If the typed name matches:
1. Token is encrypted with Fernet and stored in `bot_instances.token_encrypted`
2. Username is stored in `bot_instances.username`
3. `updated_at` is set to now
4. An audit log entry is created: `BOT_TOKEN_CHANGED` with instance_id
5. A banner appears: "⚠️ توکن ذخیره شد. برای اعمال تغییرات، سرویس باید ریستارت شود."

## Restart requirement

Token changes are persisted immediately to the database but do NOT take
effect until the process restarts. This is because:

1. aiogram's `start_polling()` can't add/remove bots at runtime
2. `BotRegistry` is built once at startup

The admin panel shows a persistent banner after any token change:

```
⚠️ تغییرات توکن ذخیره شده ولی هنوز اعمال نشده.
برای اعمال، سرویس را ریستارت کنید.
```

This banner is shown by comparing `bot_instances.updated_at` against the
process start time (from `runtime_status`).

## API endpoints

```
GET  /bots                     — render bot_tokens.html
POST /bots/{id}/token          — save token (step 1: validate format)
POST /bots/{id}/token/confirm  — confirm save (step 2: match display_name)
POST /bots/{id}/toggle         — toggle is_active
```

## Security

- Tokens are NEVER returned to the frontend after saving. The edit modal
  always shows an empty field, not the current token.
- Tokens are never logged, never included in error messages.
- The confirmation step prevents wrong-slot errors.
- Audit log records who changed what, when.
- Only `OPERATIONS_VIEW` (Super Admin) can access this page.
