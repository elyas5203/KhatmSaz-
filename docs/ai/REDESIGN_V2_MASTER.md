# KhatmSaz Redesign V2 Master Document

This document outlines the complete, definitive architecture for the Khatm models, participation flows, and reminder/delivery systems, based on the user's detailed specification on 2026-10-03.

## 1. Khatm Creation (Creator Bot)

When a Creator creates a Khatm, they must choose the fundamental **Khatm Mode**:

### A. Open Mode (????)
- **Concept:** No religious obligation (??? ????) on the members.
- **Creator Settings:** The creator does NOT set a fixed daily amount. The choice of how to participate is entirely left to the member.
- **Member Flow:** When joining, members are presented with the **Participation Mode Picker** (see Section 2).

### B. Commitment Mode (?????)
- **Concept:** Members take on a religious obligation.
- **Creator Settings:**
  1. The creator specifies the **Total Goal** (e.g., 14, 313, 110, or custom).
  2. The creator chooses the **Commitment Policy**:
     - **Fixed by Creator (????? ????):** The creator specifies the exact daily amount (e.g., 10 Salawats per day, or 2 pages of Quran per day).
     - **Member Choice (????? ??? ?????):** The creator allows the members to decide their own commitment.
- **Member Flow:**
  - If **Fixed by Creator**: The member is shown the fixed amount and the religious obligation warning. If they accept, they are ONLY asked for their preferred **Delivery Time**. They do NOT see the Participation Mode Picker.
  - If **Member Choice**: The member is shown the religious obligation warning. If they accept, they are shown the **Participation Mode Picker** (see Section 2).

---

## 2. Participation Mode Picker (Member Bot)

If the Khatm is Open, OR if it is a Member-Choice Commitment Khatm, the joining member is asked how they want to participate:

### Option 1: Numeric / Reservation (?????? / ????)
- **Concept:** The user reserves a specific chunk of the total goal to complete within 7 days.
- **Flow:**
  1. Bot asks: "How much do you want to read/say?" (e.g., 200).
  2. The user enters the number.
  3. **Reservation:** This amount is instantly reserved and deducted from the available capacity of the Khatm.
  4. **Delivery:** The bot immediately sends a message with the content (text/audio/file) and a ? ????? ??? (Done) button. The message states: "This portion is reserved for you for exactly 7 days."
  5. **Completion:** When the user clicks "Done", the portion is marked as completed (and permanently deducted from the total goal).
  6. **Expiration & Reminder:**
     - On **Day 6** (one day before expiration), if the user hasn't clicked "Done", the bot sends a reminder: "Your reserved portion expires tomorrow. Please complete it."
     - On **Day 7** (expiration), if still not done, the reservation is cancelled, and the amount is returned to the Khatm's available capacity for others to take.

### Option 2: Regular Schedule (????)
- **Concept:** The user commits to a recurring schedule. Portions are NOT reserved in advance. They are generated and sent at the scheduled times, and only deduct from the total goal when the user clicks "Done".
- **Flow:**
  1. Bot asks: "Do you want this every day, or on specific days of the week?"
     - *If Specific Days:* User selects the days (e.g., Sat, Mon, Fri).
  2. Bot asks: "At what time should we send it?"
  3. Bot asks: "How much do you want to read/say per delivery?"
  4. **Summary:** Bot confirms: "You will receive [Amount] at [Time] on [Days]."
  5. **Delivery:** At the exact scheduled time, the bot sends the content (text/audio/file) with a ? ????? ??? (Done) button.
  6. **Completion:** When the user clicks "Done", that specific delivery is marked as completed and deducted from the total goal.
  7. **Missed Delivery Reminder:** If **2 hours** pass after the delivery message was sent and the user hasn't clicked "Done", the bot sends a reminder.
     - *UX Detail:* To keep the chat clean, the reminder does NOT duplicate the content. It contains a "View Portion" button that links directly to the original delivery message. Once the user clicks "Done" on the original message, the reminder message is automatically deleted.

---

## 3. UI/UX Rules

- **The "Done" Button Location:** The ? ????? ??? button must ONLY appear attached to the actual content message (the file, audio, or text of the portion). It must NEVER appear under the Welcome message or any other informational message.
- **Welcome Message Cleanup:** For Fixed Commitment Khatms, the warning message ("This is a commitment... if you are sure, confirm") should be DELETED once the user clicks confirm, to avoid cluttering the chat history.
- **Bot Separation:** KhatmSaz (Creator Bot) is strictly for creating and managing Khatms. Members MUST use the specific Member Bots to join, receive reminders, and interact with portions.

---

## 4. Current Implementation Status vs V2 Redesign

- **Current Flaws:**
  - The Numeric (??????) mode currently doesn't implement the 7-day reservation system properly. It just asks for a number and acts as a one-off log, without the Day 6 reminder or Day 7 expiration.
  - The Regular (????) mode currently lacks the "Specific Days of the Week" picker (it defaults to daily for everything except some specific old logic).
  - The 2-hour missed delivery reminder with deep-linking is completely unbuilt.
  - The Creator Fixed Daily Commitment currently doesn't correctly skip the mode picker in all cases, or fails to properly enforce the daily delivery logic for non-Quran khatms.
  - The "Done" button was leaking onto welcome messages (mostly fixed in recent patches, but needs systemic enforcement).

## 5. Execution Plan

Once approved, the implementation will proceed in the following phases:
1. **Phase 1: DB Schema & Models Update.** Add fields for 7-day expirations on reservations, specific weekdays on schedules, and missed-reminder tracking.
2. **Phase 2: Member Mode Picker & Numeric Flow.** Build the true 7-day reservation flow, Day 6 reminder cron, Day 7 expiration cron.
3. **Phase 3: Regular Schedule Flow.** Build the specific-days picker, schedule the deliveries, and implement the 2-hour missed reminder with deep linking and auto-deletion.
4. **Phase 4: Creator Fixed Mode.** Ensure the Creator Fixed mode smoothly asks for time only and integrates seamlessly with the Regular Delivery engine.
