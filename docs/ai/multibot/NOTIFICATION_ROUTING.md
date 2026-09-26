# NOTIFICATION ROUTING — Sending via the Correct Bot

## Problem

In the old single-bot architecture, all notifications went through one
Telegram bot and one Bale bot. Now there are 26 bots — a notification must
be sent through the bot the member is actively using.

## Which bot sends what?

| Notification type | Sent from | How to resolve |
|-------------------|-----------|---------------|
| Daily portion reminder | Member bot | participation.joined_via_bot_instance_id |
| Portion content delivery | Member bot | participation.joined_via_bot_instance_id |
| Completion confirmation | Member bot | participation.joined_via_bot_instance_id |
| Miss notice to creator | Creator bot | khatm.creator → platform_identity → creator bot |
| Join request to creator | Creator bot | creator's platform_identity |
| Broadcast to members | Member bots | each participation.joined_via_bot_instance_id |
| Admin system message | Creator bot | always creator bot |
| Monthly report | Member bot(s) | one report per bot the user is active in |

## Tracking: `joined_via_bot_instance_id`

New column on `khatm_participations`:

```sql
ALTER TABLE khatm_participations
    ADD COLUMN joined_via_bot_instance_id UUID REFERENCES bot_instances(id);
```

Set when a user joins a khatm through a member bot's `/start join_{TOKEN}`
handler. For existing participations (created before multi-bot), this is NULL.

## Notify function signature

The `notify_fn` callback changes from:

```python
# OLD
async def notify(platform_value: str, chat_id: str, text: str) -> None

# NEW
async def notify(platform_value: str, chat_id: str, text: str,
                 *, bot_instance_id: UUID | None = None) -> None
```

Behavior:
- If `bot_instance_id` is provided → use that specific bot
- If `bot_instance_id` is None → fall back to creator bot for that platform
  (backward compatible with old code paths)

## Reminder engine changes

**File**: `src/khatmsaz/modules/reminder_engine/service.py`

The reminder engine already loops over participations. For each participation
that needs a notification:

```python
bot_instance_id = participation.joined_via_bot_instance_id
await notify(
    platform_identity.platform.value,
    platform_identity.platform_user_id,
    reminder_text,
    bot_instance_id=bot_instance_id,
)
```

If `joined_via_bot_instance_id` is NULL (legacy participation), the notify
function falls back to the creator bot — the member will get the notification
from the creator bot, which is acceptable during migration.

## Broadcast routing

When a creator sends a broadcast to all members of their khatm:

1. Load all participations for the khatm
2. Group by `joined_via_bot_instance_id`
3. For each group, send using the corresponding bot
4. For NULL group (legacy), use creator bot

## Deriving bot instance (fallback)

When `joined_via_bot_instance_id` is NULL, the system CAN derive the correct
bot from:

1. Khatm → `resolve_bot_category()` → category
2. User → `user_settings.language` → language (best guess)
3. Platform identity → platform

Then: `registry.get_member_bot(platform, category, language)`

This is a fallback only. New participations always have
`joined_via_bot_instance_id` set explicitly.

## Cross-bot notifications

Some notifications go to a user who is on a DIFFERENT bot than where the
action happened:

- **Creator gets "member joined" notification**: sent via creator bot
  (look up creator's platform_identity, use creator bot)
- **Creator gets "miss notice"**: sent via creator bot
- **Member gets "creator approved your join request"**: sent via the member
  bot the join request was made through (stored on the join request record)

The pattern: always use the bot that matches the RECIPIENT's context, not
the SENDER's context.

## `notify_adapter.py` changes

```python
def build_notify_fn(registry: BotRegistry) -> NotifyFn:
    async def _notify(platform_value, chat_id, text, *,
                      bot_instance_id=None):
        if bot_instance_id:
            bot = registry.get_by_instance_id(bot_instance_id)
        else:
            bot = registry.get_creator_bot(Platform(platform_value))
        if not bot:
            logger.warning("No bot for %s/%s", platform_value, bot_instance_id)
            return
        await bot.send_message(int(chat_id), text, parse_mode="HTML")
    return _notify
```

The `build_send_quran_pages_fn` similarly takes a `bot_instance_id` parameter
to send Quran page images/audio from the correct member bot.
