# MASTER-29: Broadcast Dynamic Package Size Architecture & Advertising Reward Removal

> **Date:** 2026-10-15  
> **Status:** APPROVED & IMPLEMENTED  
> **Author:** Antigravity  
> **Context:** KhatmSaz (ختم‌ساز) — Admin Panel & Broadcast System Refinement  

---

## 1. Executive Summary & Owner Mandate

### 1.1 Owner Request
> «این نرخ پاداش میخوام حدف بشه برام به صورت کامل اینو نمیخوام  
> بعد تعداد بسته هم بتونم مشخص بکنم که مثلا 100 تا باشه یا 1000 یا 7374 اینطوری میخوام باشه  
> بعد ی طوری درست بکن ک همه جا درست باشه فایل مسترشم درست بکن برام»

### 1.2 Core Problem Analysis & Scope
1. **Ad Reward Rate Abolition:**
   - In the Web Admin Finance Panel (`/finance`, Tab 5), the card `💰 نرخ پاداش تبلیغات خدمتگزاران` allowed configuring a reward amount (in Tomans) paid to creators for delivered ads.
   - The owner explicitly mandated the complete removal of this card, concept, and reward mechanism.
2. **Dynamic / Configurable Broadcast Package Size:**
   - Previously, broadcast messaging costs were hardcoded to fixed tiers of 1,000 recipients:
     $$\text{Packages} = \left\lceil \frac{\text{Audience}}{1000} \right\rceil$$
   - The owner required arbitrary and flexible package sizing (e.g., 100, 1000, 7374, etc.) per communication channel (Telegram, Bale, SMS).
   - The admin must be able to specify both the **package size (recipient count per package)** and the **price per package** directly from the Web Admin Panel.
   - The Creator Bot (`@Khatm_Saz_bot`) and Creator Web Panel (`/creator/broadcasts`) must dynamically reflect the configured package size and compute required packages accurately.

---

## 2. Technical Architecture & Domain Rules

### 2.1 Ad Reward Rate Removal
- **UI Elimination:**
  - Removed `<!-- Ad Reward Rate Form -->` card from `src/khatmsaz/web/templates/finance.html`.
  - Renamed Tab 5 from `📢 پیامک، ارسال گروهی و پاداش تبلیغات` to `📢 پیامک و ارسال گروهی`.
  - Removed `active_ad_rate` from `/finance` context and queries in `src/khatmsaz/web/app.py`.
- **Bot Handler Deprecation:**
  - Deprecated `/admin_ad_rate` command in `src/khatmsaz/bot/handlers/admin.py` to notify admins that ad rewards have been permanently retired.
- **Service Deactivation:**
  - Deactivated ad reward credit accrual in `src/khatmsaz/modules/advertising/service.py`.

### 2.2 Broadcast Dynamic Package Size Architecture
- **System Settings Configuration (`src/khatmsaz/modules/system_settings/service.py`):**
  Added three new whitelisted settings to `KNOWN_SETTINGS`:
  - `broadcast_telegram_package_size`: Default 1,000 (min: 1, max: 10,000,000).
  - `broadcast_bale_package_size`: Default 1,000 (min: 1, max: 10,000,000).
  - `broadcast_sms_package_size`: Default 1,000 (min: 1, max: 10,000,000).
- **Service Layer (`src/khatmsaz/modules/broadcast/service.py`):**
  - Added `channel_package_size(session, channel)` helper to resolve active package size with safe fallbacks.
  - Updated `submit()` calculation:
    $$\text{Packages} = \left\lceil \frac{|\text{Audience}|}{\text{package\_size}} \right\rceil$$
    $$\text{Cost} = \text{Packages} \times \text{unit\_price}$$
  - Dynamic invoice description: `هزینه ارسال پیام گروهی ({packages_count} بسته {package_size:,} نفری برای {len(users)} مخاطب)`.
- **Admin Panel Web Interface (`src/khatmsaz/web/templates/finance.html`):**
  - Added dual-field form for each channel (`TELEGRAM`, `BALE`, `SMS`) in Tab 5:
    1. `package_size`: تعداد مخاطب در هر بسته (نفر) (e.g. 100, 1000, 7374).
    2. `price_toman`: هزینه هر بسته (تومان).
  - Updated endpoint `POST /finance/broadcast-policy` in `src/khatmsaz/web/app.py` to receive and persist `package_size`.
- **Creator Bot & Web Transparency:**
  - Creator Bot (`src/khatmsaz/bot/handlers/creator_broadcast.py`): Displays dynamic package size, unit price, required packages count, and total estimated cost before composing the message.
  - Creator Web Panel (`src/khatmsaz/web/templates/creator_broadcasts.html`): Displays dynamic package size in channel selection dropdown options.

---

## 3. Verification & Automated Test Coverage

The test suite `tests/test_master_29_broadcast_package_size.py` validates all aspects of the implementation:
1. `test_system_settings_broadcast_package_size_keys`: Validates key registration and constraints.
2. `test_channel_policy_and_package_size`: Validates resolution of channel pricing and package sizing.
3. `test_broadcast_submit_custom_package_size_100`: Validates package calculation with 100-recipient batch size.
4. `test_broadcast_submit_custom_package_size_7374`: Validates package calculation with arbitrary 7374-recipient batch size.
5. `test_web_admin_update_broadcast_policy_saves_package_size`: Validates admin web form submission and persistence.

All tests passed with 100% success rate.
