# MASTER-59: Unified Collective Quran Progression Relay, Round Wrap-Around & Unread Portions Reminder Engine

## 1. Overview & Context
In KhatmSaz group khatms, Quran recitations in commitment mode (`COMMITMENT`) require a unified collective progression model ("سیر دسته‌جمعی"):
1. **Collective Progression Relay (سیر دسته‌جمعی در حالت تعهدی):**
   When multiple participants join a commitment Quran khatm, reading portions advance collectively like a relay across the group rather than staggering isolated personal offset intervals:
   - Participant 1 receives pages 1 to 3 (aligned to the canonical reciter's audio boundary for message 12).
   - Participant 2 receives pages 4 to 5.
   - On the next delivery cycle, Participant 1 receives pages 6 to 7 (continuing immediately from where the collective cursor left off).
2. **Unread Previous Portion Reminder (یادآوری سهم گذشته):**
   When delivering today's scheduled portion, if the member has outstanding uncompleted shares from prior days, the delivery message appends a clear, warm Persian reminder notice:
   `⚠️ یادآوری سهم گذشته: شما هنوز صفحات {pages} از نوبت قبل را تأیید نکرده‌اید؛ لطفاً آن را هم قرائت فرمایید. 🌱`
   Today's portion is delivered normally, ensuring that daily progression is never halted.
3. **Multi-Round Wrap-Around & Completion (چرخش دورها از صفحه ۱):**
   When the collective progression cursor reaches the end of the Quran (page 604), it seamlessly wraps around back to page 1 for the next round. If `repetition_target` is configured (either in total pages or rounds), the khatm automatically completes and announces completion once all target rounds have been recited.

---

## 2. Architectural Blueprint

### A. Collective Progression Relay in Allocation & Delivery
- **Audio Boundary Alignment:** In the canonical 604-page Madina-Hafs Quran (`CANONICAL_EDITION_ID`), audio message 12 covers pages 1 through 3 combined. For standard 2-page commitment portions (`amount == 2`), the initial portion from page 1 must span pages 1–3, and portion 301 at page 602 spans 602–604. Subsequent intermediate portions span exact pairs (`4–5`, `6–7`, ...).
- **Relay Cursor Calculation:**
  In `allocation_repository.allocate_page_amount` and `share_occurrence.delivery.get_next_open_quran_page`, the cursor is derived from the latest portion/occurrence across the whole khatm plan, ensuring smooth continuous handoff between all participants.
- **Round Wrap-Around:**
  `(last_end % total_pages) + 1`: Page 604 wraps back to page 1.

### B. Unread Previous Portion Detection & Notification
- Helper `list_uncompleted_previous_occurrences(session, participation_id, current_occurrence_id)` discovers previous delivered occurrences with `completed_at IS NULL`.
- In `occurrence_adapter.py`:
  - `format_unread_reminder(unread_occurrences)` generates the exact owner-approved Persian copy.
  - In `deliver_occurrence`, the reminder is appended to the final component caption or message text right beside the completion action button.
  - In `send_control` (ACTION purpose), the reminder is appended to the control message text.

### C. Multi-Round Target & Khatm Completion
- In `delivery.py` (`prepare`, `prepare_numeric`, `record_progress`), `repetition_target` is normalized against `total_pages`.
- If `repetition_target < total_pages` (e.g. 1, 2, 3 rounds), it is scaled to `target * total_pages`.
- When `total >= target`, the khatm is marked `COMPLETED` by `khatm_service.complete_khatm`.

---

## 3. Database & State Invariants
- No schema migration needed: `uq_portion_participant_sequence` indexes `(plan_id, participation_id, sequence)` where `participation_id IS NOT NULL`, allowing sequences to advance indefinitely across rounds while `unit_start` repeats across rounds.
- Idempotency preserved: `delivered_at` receipts prevent message duplication.
