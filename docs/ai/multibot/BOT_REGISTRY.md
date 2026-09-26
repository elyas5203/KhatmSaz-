# BOT REGISTRY — Database & Runtime

## Database table: `bot_instances`

Stores the 26 bot definitions and their encrypted tokens.

```sql
CREATE TABLE bot_instances (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform        VARCHAR(10) NOT NULL,       -- 'TELEGRAM' | 'BALE'
    bot_role        VARCHAR(10) NOT NULL,       -- 'CREATOR' | 'MEMBER'
    category        VARCHAR(20),                -- 'QURAN' | 'SALAWAT' | 'DUA_ZIYARAT' | 'LAAN' (NULL for CREATOR)
    language        VARCHAR(2),                 -- 'fa' | 'ar' | 'en' (NULL for CREATOR)
    token_encrypted TEXT NOT NULL DEFAULT '',    -- Fernet-encrypted bot token (empty = not configured)
    username        VARCHAR(100) NOT NULL DEFAULT '',  -- bot username without @
    display_name    VARCHAR(200) NOT NULL,       -- human-readable label
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(platform, bot_role, category, language)
);
```

**Pre-seeded**: the migration inserts 26 rows with empty tokens. The admin
fills them in via the web panel (`/bots`).

## Token encryption

Bot tokens are sensitive credentials. They are encrypted at rest using
[Fernet](https://cryptography.io/en/latest/fernet/) symmetric encryption.

- **Encryption key**: env var `BOT_TOKEN_ENCRYPTION_KEY` — a Fernet key
  generated once with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`.
- **Encrypt on write**: `service.set_token(instance_id, raw_token)` encrypts
  and stores.
- **Decrypt on read**: `service.get_token(instance_id)` decrypts and returns.
  Used only at startup (bootstrap) and never logged.
- Creator bot tokens are ALSO stored in `.env` for bootstrapping (the process
  needs at least one token before it can read the DB). At startup, bootstrap
  syncs the `.env` tokens into the `bot_instances` table.

## Module structure

```
src/khatmsaz/modules/bot_registry/
├── __init__.py
├── models.py       # BotInstance ORM model, BotRole enum, BotCategory enum
├── repository.py   # CRUD: list_active, get_by_id, set_token, update_username
├── service.py      # encrypt/decrypt tokens, resolve_bot_category(khatm),
│                   #   list_configured_member_bots, sync_creator_from_env
```

## Runtime: `BotRegistry` class

**File**: `src/khatmsaz/core/bot_registry.py`

A singleton built at startup. Holds live `Bot` instances indexed multiple ways:

```python
class BotRegistry:
    _bots_by_id: dict[UUID, Bot]
    _creator_bots: dict[Platform, Bot]
    _member_bots: dict[tuple[Platform, BotCategory, str], Bot]

    def get_creator_bot(platform: Platform) -> Bot | None
    def get_member_bot(platform: Platform, category: BotCategory, lang: str) -> Bot | None
    def get_by_instance_id(instance_id: UUID) -> Bot | None
    def all_bots() -> list[Bot]
    def creator_bots() -> list[Bot]
    def member_bots() -> list[Bot]
```

Each `Bot` object carries custom attributes set at build time:

| Attribute | Type | Example |
|-----------|------|---------|
| `bot.khatmsaz_platform` | `Platform` | `Platform.TELEGRAM` |
| `bot.khatmsaz_role` | `BotRole` | `BotRole.MEMBER` |
| `bot.khatmsaz_category` | `BotCategory \| None` | `BotCategory.QURAN` |
| `bot.khatmsaz_language` | `str \| None` | `"fa"` |
| `bot.khatmsaz_instance_id` | `UUID` | `...` |

## Startup flow

1. Load creator bot tokens from `.env` (existing behavior)
2. Open DB session → `bot_registry_service.sync_creator_from_env(session)`
   - Upserts creator bot rows in `bot_instances` from `.env` values
3. `bot_registry_service.list_configured_member_bots(session)`
   - Returns all MEMBER rows where `token_encrypted != ''` and `is_active = True`
4. For each configured member bot:
   - Decrypt token
   - Build `Bot` instance via `build_telegram_bot(token)` or `build_bale_bot(token)`
   - Tag with role/category/language/instance_id
5. Build `BotRegistry` singleton from all bot instances

## Adding/changing a token at runtime

Tokens are managed via the admin web panel (see
[ADMIN_TOKEN_PANEL.md](ADMIN_TOKEN_PANEL.md)). Changes are persisted to DB
immediately but **require a process restart** to take effect (polling loops
cannot be hot-reloaded). The admin panel shows a "restart required" banner
after any token change.

## `resolve_bot_category(khatm)` function

Maps a `Khatm` object to a `BotCategory`:

```python
def resolve_bot_category(khatm: Khatm, category: KhatmCategory | None) -> BotCategory:
    if khatm.template_type in (KhatmTemplateType.QURAN_PAGE,
                                KhatmTemplateType.QURAN_SURAH,
                                KhatmTemplateType.SURAH):
        return BotCategory.QURAN

    if category and category.group == KhatmCategoryGroup.LAAN:
        return BotCategory.LAAN

    if khatm.template_type in (KhatmTemplateType.DUA,
                                KhatmTemplateType.ZIYARAT):
        return BotCategory.DUA_ZIYARAT

    if category and category.group == KhatmCategoryGroup.DUA:
        return BotCategory.DUA_ZIYARAT

    # SALAWAT template with SALAWAT group, or default
    return BotCategory.SALAWAT
```
