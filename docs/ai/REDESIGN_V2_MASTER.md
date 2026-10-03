## 2026-10-03 — Urgent reminder regression [Codex]
- [x] Diagnose repeated La'an content / missing Done action: `reminder_text` returned None for Persian; `completion_text` also missed its return.
- [x] Restore returns and Quran audio hint; request persistent member menu.
- [x] Regression: two daily scans, one nonempty action with regular_done callback, one content send.
- [ ] Live deployment/verification (not performed). Full suite: 297 passed, 11 pre-existing failures, 94 skipped. Existing migration history has multiple heads; no new migration in this fix.

# KhatmSaz Redesign Master Document

This document tracks the ongoing rewrite and UX fixes for the KhatmSaz V2 Redesign.

## Completed Tasks

1. **Waitlisted Mode & Delivery Hour Prompts (Phase 4):**
   - Waitlisted members were missing the prompt for delivery hour and pages/day when approved.
   - **Fix:** Patched `join_requests.py` to trigger the member setup flow when an admin approves them.
2. **Fixed Commitment Custom Portions:**
   - The bot failed to track completion of Non-Quran Fixed Commitment portions because `mark_portion_done` explicitly checked for `KhatmTemplateType.QURAN_PAGE`.
   - **Fix:** Removed the strict QURAN check in `mark_portion_done` to support all portion types.
3. **Commitment Consent Warning Cleanup:**
   - The warning message "⚠️ توجه: این ختم تعهدی است..." lingered in the chat after the member accepted or cancelled the commitment.
   - **Fix:** Patched `join_flow.py` to delete the message via `callback.message.delete()` upon accepting/cancelling.
4. **Erroneous "✅ انجام سهم" (Done) Button on Success/Welcome Messages:**
   - The bot attached the open-reading "✅ انجام سهم" button inappropriately on welcome messages and progress success messages.
   - If clicked on a Fixed Commitment Khatm, this caused the bot to incorrectly ask "How many pages did you read?" (Image 3 bug).
   - **Fix:** Removed `contribute_keyboard` from welcome messages in `start.py` (for waitlisted, commitment, and scheduled open khatms).
   - **Fix:** Removed `commitment_quantity_keyboard` from the success message in `portions.py` (for count commitments). The Done button must strictly appear only under the Khatm content itself.
5. **Audio Settings Notice:**
   - Members were receiving Quran audio by default but lacked guidance on how to turn it off.
   - **Fix:** Patched `reminder_text` in `member_copy.py` to dynamically append "💡 برای خاموش کردن دریافت صوت قرآن، می‌توانید به بخش تنظیمات ربات مراجعه کنید." when delivering Quran portions with audio enabled.

## Notes & Clarifications
- **Creator Fixed Amount Prompt:** The system *does* currently ask the creator for the exact daily amount (e.g., "چند صفحه روزانه بخونه مثلا 2 صفحه") when they select the `FIXED_AMOUNT` policy. The issue reported in "Image 3" was not the lack of this setting, but rather the member being incorrectly prompted for an amount due to the erroneous `✅ انجام سهم` button being present on their welcome card.
