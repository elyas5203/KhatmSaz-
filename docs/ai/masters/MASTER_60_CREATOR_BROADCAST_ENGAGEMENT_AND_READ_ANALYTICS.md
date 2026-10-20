# MASTER-60 — Creator Broadcast Engagement, Delivery Receipts & Live Seen/Activity Tracking System

## 1. Overview & Context

- **Goal:** Provide khatm creators with comprehensive, real-time feedback and read analytics on group broadcast messages (پیام‌های گروهی سازنده) sent to their members.
- **Owner Clarification & Behavioral Rules:**
  - **Clean Recipient Experience:** Audience messages must remain completely pure and clean — strictly **no** extra buttons, text or confirmation prompts appended to the recipient's message.
  - **Seamless Read/Seen Tracking (سین / تیک دوم):** Because Telegram and Bale Bot APIs do not provide read-receipt webhooks for standard bot messages, member seen status is determined non-intrusively via user in-bot activity (any message, command, portion confirmation, or callback after delivery).
  - **Creator Confirmation & Live Report:** When an approved broadcast is sent, the creator immediately receives a confirmation notification in their bot with an interactive inline button `[📊 مشاهده آمار بازخورد و سین]`.
  - **Live In-Place Refresh:** The creator can tap `[🔄 بروزرسانی آمار]` to refresh counts, percentages, and seen statuses in place with live timestamps.
  - **Recipients List:** Creator can view paginated recipient delivery and seen status.
  - **Web Admin Integration:** The Web Admin `/broadcasts` tab 2 (History) displays seen counts and engagement percentages alongside delivery metrics.

---

## 2. Architectural Design

```mermaid
flowchart TD
    Admin[Admin / Web Approver] -->|Approve Broadcast| DeliveryEngine[deliver_broadcast Service]
    DeliveryEngine -->|Send Clean Message/Media| Members[Target Audience Members]
    DeliveryEngine -->|Create Receipts| DB[(khatm_broadcast_receipts)]
    DeliveryEngine -->|Notify Creator| CreatorBot[Creator Bot Chat]
    CreatorBot -->|Sends Message + Inline Button| Creator[Khatm Creator]

    Members -->|Any Bot Action / Portion Confirm| ModerationMiddleware[Bot Middleware / Handlers]
    ModerationMiddleware -->|Mark Seen| DB

    Creator -->|Taps [📊 آمار بازخورد و سین]| StatsHandler[cbroadcast:stats Handler]
    StatsHandler -->|Read Real-Time Stats| DB
    StatsHandler -->|Renders Live Report Card| Creator
    Creator -->|Taps [🔄 بروزرسانی آمار]| RefreshHandler[cbroadcast:refresh Handler]
    RefreshHandler -->|Updates In-Place| Creator
```

---

## 3. Database Schema

### Table: `khatm_broadcast_receipts`
- `id` (UUID, Primary Key)
- `broadcast_id` (UUID, FK -> `khatm_broadcasts.id` ON DELETE CASCADE, Indexed)
- `recipient_user_id` (UUID, FK -> `users.id` ON DELETE CASCADE, Indexed)
- `channel` (VARCHAR(16), Default 'TELEGRAM')
- `status` (VARCHAR(20), Default 'DELIVERED') — `DELIVERED`, `SEEN`, `FAILED`
- `delivered_at` (TIMESTAMPTZ, Default NOW())
- `seen_at` (TIMESTAMPTZ, Nullable)
- `seen_source` (VARCHAR(32), Nullable) — `BOT_ACTIVITY`, `PORTION_CONFIRM`, `REACTION`
- Index: `ix_khatm_broadcast_receipts_user_seen` on `(recipient_user_id, seen_at)`
- Index: `ix_khatm_broadcast_receipts_bc_status` on `(broadcast_id, status)`

---

## 4. Wording & Copy Rules (Warm Plain Persian)

### Creator Notification upon Delivery:
```text
📢 پیام گروهی شما با موفقیت برای اعضا ارسال شد!

🕋 ختم: «{khatm_title}»
👥 تعداد دریافت‌کنندگان: {total} نفر
📅 زمان ارسال: {date_time}

جهت مشاهده تعداد اعضایی که پیام را باز کرده و مشاهده کرده‌اند، دکمه زیر را لمس فرمایید:
```
Button: `[📊 مشاهده آمار بازخورد و سین]` (`cbroadcast:stats:{broadcast_id}`)

### Live Stats Report Card:
```text
📊 گزارش تحویل و مشاهده پیام گروهی

🕋 ختم: «{khatm_title}»
📝 نوع پیام: {media_title}
📅 زمان ارسال: {sent_time}

👥 کل مخاطبان: {total} نفر
📥 تحویل داده شده: {delivered} نفر ({delivered_pct}٪)
👁 مشاهده شده (سین خورده): {seen} نفر ({seen_pct}٪)
⏳ در انتظار مشاهده: {unseen} نفر ({unseen_pct}٪)
{media_note}

🔄 آخرین بروزرسانی: {current_time}
```
Buttons:
- `[🔄 بروزرسانی آمار]` (`cbroadcast:refresh:{broadcast_id}`)
- `[👥 اسامی مخاطبان]` (`cbroadcast:recipients:{broadcast_id}:0`)
- `[🔙 بازگشت به منو]` (`cbroadcast:menu`)

---

## 5. Verification & Test Suite

- Database migration applied and validated.
- Clean delivery to audience without buttons or appended text.
- User activity triggers `record_user_seen`.
- Live stats calculation and refresh functionality.
- Web Admin history view displays seen metrics.
