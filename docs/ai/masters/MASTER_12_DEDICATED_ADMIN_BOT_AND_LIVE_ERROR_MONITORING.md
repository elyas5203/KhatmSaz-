# MASTER-12: Dedicated Admin Bot (@khatmsaz_admin_bot), Real-Time Crash Monitoring & Custom La'n Wizard Flow

**Status:** APPROVED BY OWNER  
**Date:** 2026-10-13  
**Decisions Recorded:** `DEC-PY-0125` (Dedicated Admin Bot & Creator Bot Isolation), `DEC-PY-0126` (Real-Time Error Logging & Telegram Crash Dispatch), `DEC-PY-0123` (Custom La'n Wizard & Auto Invite Dispatch), `DEC-PY-0124` (Direct PayPing Shaparak Link & 8-Digit Tracking Code)

---

## 1. Executive Summary & Purpose

In accordance with direct owner instructions (2026-10-13):
1. **Dedicated Admin Bot (`@khatmsaz_admin_bot`):**
   - **Bot Token:** `8804225228:AAHPfsV4E8oSxjoGSqpD4S3GgkPJxuZKEH4`
   - **Username:** `@khatmsaz_admin_bot`
   - **Isolation of Creator Bot (`Khatm_Saz_bot`):** The creator bot is now **strictly and exclusively** for creating and managing khatms. Even the Super Admin using `Khatm_Saz_bot` sees only the creator role and wizard. All admin notifications, moderation queues, receipt approvals, bug alerts, and settings move into the dedicated Admin Bot.
   - **Role Gate:** Only the Super Admin (Telegram ID `5490508090` / `SUPER_ADMIN` in DB) can access `@khatmsaz_admin_bot`. All other users receive an unauthorized access notice.
2. **Real-Time Logging & Crash Alert System:**
   - **Persistent File Logging:** Continuous moment-by-moment logging into `logs/khatmsaz.log` (rotating, 10MB x 5 backups) and `logs/errors.log` (errors & critical exceptions).
   - **Immediate Telegram Crash Alerts:** Any `ERROR` or `CRITICAL` log record, or unhandled exception in `asyncio` or `sys.excepthook`, is formatted and dispatched in real time to the Super Admin via `@khatmsaz_admin_bot`.
   - **Interactive Log Viewer:** Commands `/logs`, `/errors`, and `/get_log_file` inside `@khatmsaz_admin_bot`.
3. **Custom La'n Creation Wizard & Automatic Invite Delivery:**
   - Removal and purge of all preset La'n categories («لعن عمر», «لعن ابوبکر», «لعن عایشه», «لعن هشت‌گانه امام رضا») from the bot and database.
   - Wizard questions:
     - Question 1: «عنوان ختم لعنتون چیه؟» (Custom title).
     - Question 2: «متن ختم لعن رو بفرستید:» (Custom dhikr text).
     - Standard wizard questions (Commitment vs Free, daily amount, schedule/deadline, niyyat).
   - Saved as draft with `pending_lan_approval = True`.
   - Moderation card sent to Super Admin in `@khatmsaz_admin_bot`.
   - Upon admin approval: Khatm is activated, and the ready-to-forward invitation card with the join link is **automatically delivered to the creator**.
4. **Direct Shaparak Payment Link & 8-Digit Tracking Code:**
   - Direct link: `https://ppng.ir/d/VFBD`.
   - Bank card number and holder name completely removed from top-up screen.
   - Tracking code format: Clean 8-digit numeric code (e.g. `83491205`).
   - Receipt review with inline `[✅ تأیید و شارژ]` and `[❌ رد]` dispatched to `@khatmsaz_admin_bot`.

---

## 2. Architecture & Data Flow

```mermaid
flowchart TD
    subgraph Users & Creators
        Creator[👤 Creator / User] -->|Creates Khatm| CreatorBot[🤖 Khatm_Saz_bot\n(Creator Bot Only)]
        Creator -->|Uploads Bank Receipt| CreatorBot
    end

    subgraph Core System
        LoggingEngine[📝 Logging Engine\nlogs/khatmsaz.log\nlogs/errors.log]
        DB[(PostgreSQL)]
        AlertHandler[🚨 TelegramErrorAlertHandler]
        LoggingEngine -->|Error / Critical| AlertHandler
    end

    subgraph Admin Bot Architecture
        AlertHandler -->|Real-Time Alert| AdminBot[🛡 @khatmsaz_admin_bot\nDedicated Admin Bot]
        CreatorBot -->|Receipt Upload| AdminBot
        CreatorBot -->|Custom La'n Khatm| AdminBot
        AdminBot -->|Moderation Decision| DB
        AdminBot -->|On La'n Approval: Auto Send Invite Card| Creator
        Admin[👑 Super Admin\n(5490508090)] <-->|Commands & Inlines| AdminBot
    end
```

---

## 3. Work Packages

| WP | Scope | Description |
| :--- | :--- | :--- |
| **WP-01** | **Admin Bot Registry & Config** | Configure `admin_bot_token`, `BotRole.ADMIN`, and register in `BotRegistry`. |
| **WP-02** | **Continuous Logging & Alert Engine** | Create `logging_system.py`, rotating files, exception hooks, real-time alert dispatcher. |
| **WP-03** | **Admin Bot Dispatcher & Router** | Create dedicated `dp_admin`, gatekeeper middleware, dashboard `/start`, `/status`, `/logs`, `/receipts`, `/laan`. |
| **WP-04** | **Custom La'n Wizard Redesign** | Implement Title & Text prompts in `create_khatm.py`, delete preset categories, auto-dispatch invite card on approval. |
| **WP-05** | **Direct PayPing & Tracking Code** | Remove bank card, set `https://ppng.ir/d/VFBD`, 8-digit numeric tracking code. |
| **WP-06** | **Isolation of Creator Bot** | Remove admin notifications from `Khatm_Saz_bot`; route all admin alerts to `@khatmsaz_admin_bot`. |
| **WP-07** | **Alembic Migration & Deployment** | Delete legacy LAAN category rows, deploy to VPS `91.107.137.22`, verify port 8080. |

---

## 4. Verification Checklist

1. `@khatmsaz_admin_bot` responds to Super Admin `/start` with full Persian admin dashboard.
2. Unauthorized user messaging `@khatmsaz_admin_bot` receives 403 access denied message.
3. Errors logged in `khatmsaz` trigger immediate alert in `@khatmsaz_admin_bot` with traceback.
4. Receipts uploaded show direct link `https://ppng.ir/d/VFBD`, 8-digit tracking code, and notify `@khatmsaz_admin_bot`.
5. La'n khatm wizard prompts for Title & Text, submits for review to `@khatmsaz_admin_bot`, and sends invite card to creator upon approval.
6. VPS port 8080 active; all foreign ports untouched.
