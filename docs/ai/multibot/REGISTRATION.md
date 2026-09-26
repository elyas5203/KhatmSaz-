# REGISTRATION — Two Flows

The system has two registration flows: one for creators (on the creator bot)
and one for members (on member bots). Both produce the same `User` +
`UserSettings` records in the database.

## Creator registration (creator bot)

**File**: `bot/handlers/registration.py` (existing)

| Step | Field | Input method |
|------|-------|-------------|
| 1 | Full name | Free text |
| 2 | Phone | Contact-share button (Telegram) or manual (Bale) |
| 3 | Province | Inline keyboard (31 + outside Iran) |
| 4 | City | Free text |
| 5 | Gender | Inline buttons (Male / Female) |

**Phone verification**: OTP via SMS (Kavenegar). In dev mode (`DEV_OTP=1`),
the code is shown directly in chat.

**After registration**: if no pending join, drops into creator menu. If
pending khatm creation data exists, resumes `create_and_launch_khatm`.

## Member registration (member bots)

**File**: `bot/handlers/member_registration.py` (NEW)

Same 5 steps, same fields. Differences:

| Aspect | Creator | Member |
|--------|---------|--------|
| Phone verification | OTP (SMS) | None (trust-based) |
| Language | User's chosen language | Bot's fixed language |
| After registration | Creator menu | Resume join flow |
| Bot | Creator bot | Member bot |

**Phone handling on member bots**: Telegram shows the contact-share button.
Bale users type manually. In both cases, the phone is stored as
`contact_phone` on `UserSettings` — NOT as a verified phone claim. This
matches the current participant behavior (DEC-PY-0003: only creators verify).

## Shared user identity

Both flows create/update the same `User` record. If a user registers on a
member bot first, then later tries to create a khatm on the creator bot,
they already have a `User` record — the creator bot will:

1. Recognize them as registered (name + phone already set)
2. Check if phone is verified
3. If not → trigger OTP verification before allowing khatm creation
4. If yes → proceed to creation wizard

This prevents duplicate registrations while maintaining the OTP requirement
for creators.

## Cross-bot user recognition

A user's Telegram `chat_id` is platform-scoped, not bot-scoped. The same
Telegram user has the same `chat_id` across all 13 Telegram bots. The
`platform_identities` table links `(platform, platform_user_id)` → `user_id`.

So when a user who already registered on the Quran-FA bot visits the
Salawat-FA bot for the first time:

1. `/start` → `identity_service.resolve_or_provision()` finds existing user
2. User is already registered → skip registration entirely
3. Show join preview directly

No re-registration needed. The user's profile (name, phone, province, city,
gender) is shared across all bots.
