# متاپرامپت برای Antigravity (و هر AI جدید)

> این فایل رو به‌عنوان prompt اول به Antigravity بده تا بتونه روی این پروژه کار کنه.

---

## پرامپت شروع کار برای Antigravity

```
تو داری روی پروژه KhatmSaz (ختم‌ساز) کار می‌کنی — یه بات تلگرامی و بله برای
سازماندهی ختم‌های گروهی (قرآن، صلوات، دعا، زیارت). پروژه Python هست.

**اول این فایل‌ها رو بخون (به همین ترتیب):**
1. `docs/ai/PROJECT_STATE.md` — جدیدترین وضعیت پروژه (ورودی بالا = جدیدترین)
2. `docs/ai/AI_HANDOFF_PROTOCOL.md` — قوانین همکاری بین AIها (حتماً بخون)
3. `docs/ai/BACKLOG.md` — کارهای درخواستی که هنوز ساخته نشدن
4. `docs/ai/DEPLOY.md` — نحوه push و راه‌اندازی مجدد بات روی سرور

**قوانین حیاتی:**
- بات روی سرور واقعی اجرا می‌شه و کاربران واقعی دارن باهاش کار می‌کنن
- هیچ تغییری بدون تأیید مالک push نکن
- قبل از هر push: pytest باید کامل پاس بشه
- Migration رو قبل از اجرا بخون — blindly اجرا نکن
- هیچ قانون کسب‌وکاری رو حدس نزن — اگه چیزی مبهمه، بپرس

**بعد از هر تغییر معنادار:**
1. `docs/ai/PROJECT_STATE.md` رو آپدیت کن (ورودی جدید بالای فایل)
2. `docs/ai/CHANGELOG.md` رو آپدیت کن
3. اگه تصمیم محصولی گرفته شد، در `docs/ai/DECISIONS.md` ثبت کن

**Stack:**
- Python 3.13، aiogram 3، SQLAlchemy 2.0 async + asyncpg، Alembic، PostgreSQL، Redis
- Long polling (نه webhook) — بدون نیاز به domain عمومی
- پروژه زیر `src/khatmsaz/` — هر ماژول در `modules/<name>/` با models.py، repository.py، service.py

**بات‌های در حال اجرا:**
- Telegram و Bale (هر دو از همون codebase — Bale API تلگرام-compatible)
- Scheduler هر ۱۵ دقیقه یه‌بار scan می‌کنه (ساعت‌های :00, :15, :30, :45)

**چیزی که نباید کنی:**
- `git push` بدون تأیید
- `alembic upgrade head` بدون خوندن migration
- تغییر `.env` سرور بدون هماهنگی
- اضافه کردن feature جدید که مالک نخواسته

**در انتهای هر session یه گزارش بده با این فرمت:**
```
KHATMSAZ (PY) TASK REPORT
Task            — چی ازت خواسته شد
Status          — PASS / PARTIAL / BLOCKED
What I Changed  — چی تغییر کرد
Files Changed   — لیست فایل‌ها
Commands Run    — دستوراتی که اجرا کردی
Validation      — pytest: PASS/FAIL، migration: PASS/FAIL/NOT RUN
Docs Updated    — کدوم docs/ai آپدیت شد
Decisions Added — شناسه‌های تصمیم جدید
Next Step       — یه توصیه کوتاه
```
```

---

## نکات اضافه برای مالک پروژه

- این پرامپت رو هر بار که یه session جدید با Antigravity شروع می‌کنی ارسال کن
- Antigravity باید اول `docs/ai/PROJECT_STATE.md` بخونه تا از کارهای قبلی Claude Code و Codex خبردار بشه
- اگه Antigravity یه تصمیم مهم گرفت، ازش بخواه در `docs/ai/DECISIONS.md` ثبتش کنه
- توکن بات تست رو فقط در session محلی استفاده کن — هیچ‌وقت commit نکن
