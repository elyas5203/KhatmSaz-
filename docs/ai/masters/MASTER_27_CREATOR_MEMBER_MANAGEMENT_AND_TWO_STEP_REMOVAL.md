# MASTER-27: Creator Member Management & Two-Step Removal Architecture

> **Date:** 2026-10-15  
> **Status:** APPROVED & IMPLEMENTED  
> **Author:** Antigravity  
> **Context:** KhatmSaz (ختم‌ساز) — Creator Bot Interactive Member Management & Safe Two-Step Removal  

---

## 1. Executive Summary & Owner Mandate

### 1.1 Owner Request
> «تغییرات رو رویه سرور هم میخوام ببری برام بعد  
> ی ایراد دیگه هم داره ک  
> لیست اعضا رو میبینم  
> اینجا هم اینو گفته ولی کاری نمیشه کرد این درست بکن برام بعد اگر خواستم با دوبار تایید گرفتن مثلا حذفش بکنم از لیست ی همچین چیزی»

### 1.2 Core Problem Analysis
In the Creator Bot (`@Khatm_Saz_bot`), when a khatm creator receives an alert regarding an uncommitted member (e.g. *"⚠️ در ختم «...»، همراه گرامی «...» طی ۳ روز متوالی سهم خود را ثبت نکرده‌اند. راهنما: می‌توانید با ایشان تماس گرفته یا پیام دهید و در صورت تمایل، از بخش «👥 اعضا» در مدیریت ختم وضعیت عضویت را بررسی فرمایید"*):
1. Navigating to `👥 لیست اعضا` (`creator_report:members:{khatm_id}`) previously only outputted a static, non-interactive text string of member progress.
2. The creator had no buttons to view individual participant details (phone number, current portion, reminder hour, exact misses, commitment status).
3. The creator had no way to remove an inactive or unresponsive member from the bot, even though the web panel allowed it.
4. Member removal in group religious khatms is a sensitive operation with irreversible consequences (portion re-allocation, waiting list promotion, potential member hurt feelings). Therefore, a strict **two-step confirmation flow** («با دوبار تایید گرفتن») is mandatory.

---

## 2. Technical Architecture & Constraints

### 2.1 Telegram 64-Byte Callback Data Constraint
Telegram restricts inline keyboard `callback_data` strings to a maximum of 64 bytes. Standard UUIDs with hyphens are 36 characters. Concatenating prefixes and two UUIDs (e.g. `creator_member:remove:{khatm_id}:{participation_id}`) exceeds 84 bytes and triggers `BUTTON_DATA_INVALID`.

**Solution:**
- Compact namespace `km:` (Khatm Member).
- Use 32-character hex format (`uuid.hex`) without hyphens.
- Member operations reference only `participation.id.hex`. The backend queries the `Participation` entity directly, which already references its parent `khatm_id`.
- Back-to-list references `khatm.id.hex`.

| Callback Pattern | Sample Payload | Length | Status |
| :--- | :--- | :--- | :--- |
| `km:v:{part_hex}` | `km:v:c6b3e89a502f4f8ca8f8c42b78112345` | 37 bytes | ✅ Safe (< 64B) |
| `km:ask:{part_hex}` | `km:ask:c6b3e89a502f4f8ca8f8c42b78112345` | 39 bytes | ✅ Safe (< 64B) |
| `km:conf:{part_hex}` | `km:conf:c6b3e89a502f4f8ca8f8c42b78112345` | 40 bytes | ✅ Safe (< 64B) |
| `km:do:{part_hex}` | `km:do:c6b3e89a502f4f8ca8f8c42b78112345` | 38 bytes | ✅ Safe (< 64B) |
| `km:list:{khatm_hex}` | `km:list:e3b4a25c110243e8bbcf18a221234567` | 40 bytes | ✅ Safe (< 64B) |
| `km:p:{khatm_hex}:{page}` | `km:p:e3b4a25c110243e8bbcf18a221234567:1` | 42 bytes | ✅ Safe (< 64B) |

---

## 3. User Experience & Two-Step Removal Flow

```mermaid
flowchart TD
    A["👥 لیست اعضا (List Screen)"] -->|Click Member Button| B["👤 کارت مشخصات عضو (Detail Screen)"]
    B -->|Click [❌ حذف این عضو]| C["⚠️ تأیید مرحله ۱ (Step 1 Warning)"]
    B -->|Click [🔙 بازگشت به لیست]| A
    C -->|Click [⚠️ بله، ادامه حذف]| D["🔴 تأیید نهایی مرحله ۲ (Step 2 Final Confirmation)"]
    C -->|Click [❌ انصراف]| B
    D -->|Click [🔴 تأیید نهایی و لغو عضویت]| E["⚙️ اجرا (Execute Removal)"]
    D -->|Click [❌ انصراف]| B
    E --> F["✅ اعلان موفقیت و آزادسازی سهم"]
    F -->|Click [🔙 بازگشت به لیست اعضا]| A
```

### 3.1 Screen Specifications

#### Screen 1: Interactive Member List (`km:list:{khatm_hex}` / `creator_report:members:{khatm_id}`)
- Displays active participant count, title, and paginated member list (8 members per page).
- Inline keyboard provides one button per member: `[👤 {name}]` -> `km:v:{part_hex}`.
- Pagination controls when `total_pages > 1`: `[◀️ قبلی]`, `[صفحه X از Y]`, `[بعدی ▶️]`.
- Bottom row: `[🔙 بازگشت به مدیریت ختم]` -> `my_khatms:manage:{khatm_id}`.

#### Screen 2: Member Detail Card (`km:v:{part_hex}`)
- Displays comprehensive operational details:
  - **نام کاربر (Display Name):** `member.display_name`
  - **شماره تماس (Phone):** `member_settings.contact_phone` (or "ثبت‌نشده")
  - **وضعیت تعهد (Commitment):** `متعهد 🔒` vs `آزاد / عادی 🌿`
  - **پیشرفت تلاوت (Progress):** e.g. `5/10 سهم` or `12/30`
  - **سهم جاری (Current Portion):** e.g. `صفحات 10 تا 12`
  - **ساعت یادآوری (Reminder Hour):** e.g. `14:00` or `خاموش`
  - **دیرکرد ثبت‌نشده (Miss Count):** Recorded consecutive misses in current window
- Keyboard:
  - `[❌ حذف این عضو از ختم]` -> `km:ask:{part_hex}`
  - `[🔙 بازگشت به لیست اعضا]` -> `km:list:{khatm_hex}`

#### Screen 3: Step 1 Confirmation (`km:ask:{part_hex}`)
- **Copy:**
  ```text
  ⚠️ درخواست حذف عضو (مرحله ۱ از ۲)

  آیا از حذف «{name}» از ختم «{title}» اطمینان دارید؟

  ▫️ با حذف این عضو، سهم‌های تخصیص‌یافته به ایشان آزاد خواهند شد.
  ▫️ در صورت وجود، نفر بعدی از لیست انتظار به‌صورت خودکار جایگزین می‌شود.

  جهت ادامه، دکمه «مرحله بعد» را انتخاب کنید.
  ```
- Keyboard:
  - `[⚠️ بله، ادامه حذف (مرحله ۲)]` -> `km:conf:{part_hex}`
  - `[❌ انصراف و بازگشت]` -> `km:v:{part_hex}`

#### Screen 4: Step 2 Final Confirmation (`km:conf:{part_hex}`)
- **Copy:**
  ```text
  🔴 تأیید نهایی حذف عضو (مرحله ۲ از ۲)

  ⚠️ توجه: این عملیات قطعی است و عضویت «{name}» در ختم «{title}» کاملاً لغو خواهد شد.

  آیا ۱۰۰٪ مطمئن هستید؟
  ```
- Keyboard:
  - `[🔴 تأیید قطعی و لغو عضویت]` -> `km:do:{part_hex}`
  - `[❌ انصراف و بازگشت]` -> `km:v:{part_hex}`

#### Screen 5: Execution & Clean Promotion (`km:do:{part_hex}`)
1. **Authorization Check:** Ensures caller is the authenticated creator of the khatm (`khatm.creator_user_id == user.id`).
2. **Portion Freeing:** If member holds an `ASSIGNED` portion, it is released back to `OPEN` pool via `allocation_service.release_portion`.
3. **Leave Execution:** Calls `workflow_service.leave_khatm(session, participation.id, reason="REMOVED_BY_CREATOR")`.
4. **Waiting List Promotion:** If a waiting list entry exists, it is promoted and assigned the next portion. The promoted user is notified via their platform bot.
5. **Polite Ejection Notice:** The removed member receives a courteous notification:
   > *"همراه گرامی، عضویت شما در ختم «{title}» توسط بانی ختم لغو شد. با آرزوی قبولی طاعات و عبادات شما 🤍"*
6. **Audit Trail:** Logs action `CREATOR_BOT_REMOVE_MEMBER` with `actor_user_id`, `target_user_id`, `khatm_id`, and `participation_id`.
7. **Success Screen:** Displays confirmation with `[🔙 بازگشت به لیست اعضا]` and `[⚙️ مدیریت ختم]`.

---

## 4. Verification & Testing Strategy

1. **Keyboard Generation Tests:**
   - Callback length check: Assert all generated callback strings <= 64 bytes.
   - Pagination tests: Verify multi-page splitting when members > 8.
2. **Two-Step Confirmation Flow Tests:**
   - Step 1 callback returns confirmation prompt.
   - Cancel returns to member detail view.
   - Step 2 confirmation requires explicit confirmation before calling `leave_khatm`.
3. **Execution & Promotion Tests:**
   - Unassigned portions released back to open pool.
   - Waiting list promotion occurs properly.
   - Removed user receives courteous notice.
   - Creator sees updated list without removed user.
4. **Security / Multi-tenancy Tests:**
   - Unauthorized user cannot trigger `km:v`, `km:ask`, `km:conf`, or `km:do` on another creator's khatm.

---

## 5. Production VPS Deployment Protocol

Once committed to Git branch `update_khatm_wizard_flow`:
1. SSH into VPS:
   ```bash
   ssh root@91.107.137.22
   ```
2. Navigate to project root, pull latest commits, and restart the service:
   ```bash
   cd /root/khatmsaz
   git checkout update_khatm_wizard_flow
   git pull origin update_khatm_wizard_flow
   systemctl restart khatmsaz
   systemctl status khatmsaz --no-pager
   ```
