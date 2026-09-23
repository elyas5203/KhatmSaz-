# راهنمای Deploy — پوش کد و راه‌اندازی مجدد بات روی سرور

> **هشدار حیاتی برای همه AI‌ها:** بات روی سرور (VPS) واقعی اجرا می‌شه و کاربران
> واقعی دارن باهاش کار می‌کنن. هر تغییری که push می‌شه باید:
> ۱. تست بشه (`python -m pytest` — باید همه پاس بشن)
> ۲. Migration بررسی بشه (قبل از اجرا بخونش)
> ۳. بدون تأیید مالک پروژه push نشه

---

## ۱. پوش کد به GitHub

### مرحله ۱: وضعیت تغییرات رو بررسی کن
```bash
git status
git diff
```

### مرحله ۲: تست بگیر (اجباری قبل از push)
```bash
python -m pytest
```
اگه تست fail شد — push نکن. اول مشکل رو حل کن.

### مرحله ۳: تغییرات رو stage کن
```bash
git add src/ migrations/ docs/
# یا فایل‌های خاص:
git add src/khatmsaz/modules/reminder_engine/service.py
```
**هیچ‌وقت `git add .` نزن** — ممکنه `.env` یا فایل‌های حساس اضافه بشن.

### مرحله ۴: commit
```bash
git commit -m "توضیح کوتاه تغییر"
```

### مرحله ۵: push به GitHub
```bash
git push origin main
```

---

## ۲. بکاپ قبل از push (ورژن قبلی)

Git خودش بکاپ هست — هر commit یه snapshot کامله. برای برگشت به commit قبلی:

```bash
# نمایش آخرین commitها
git log --oneline -10

# برگشت موقت به commit قبلی (بدون از دست دادن تغییرات جدید)
git stash
git checkout <commit-hash>

# برگشت دائم به commit قبلی (روی main)
git revert HEAD       # یه commit جدید می‌سازه که تغییر رو برمی‌گردونه — امن‌ترین روش
```

**هیچ‌وقت `git reset --hard` روی main اجرا نکن** بدون تأیید مالک.

اگه می‌خوای یه snapshot local هم داشته باشی:
```bash
git tag backup-before-deploy-$(date +%Y%m%d)
```

---

## ۳. آپدیت بات روی سرور VPS

وقتی push کردی، روی سرور (از طریق SSH):

### مرحله ۱: وصل شدن به سرور
```bash
ssh root@YOUR_VPS_IP
# یا اگه کلید SSH داری:
ssh -i ~/.ssh/id_rsa user@YOUR_VPS_IP
```

### مرحله ۲: رفتن به پوشه پروژه
```bash
cd /root/khatmsaz   # یا هر مسیری که هست
# اگه مطمئن نیستی:
find / -name "bootstrap.py" -path "*/khatmsaz/*" 2>/dev/null
```

### مرحله ۳: pull آخرین تغییرات
```bash
git pull origin main
```

### مرحله ۴: اگه migration جدید داری — اجراش کن
```bash
source .venv/bin/activate  # یا هر محیط مجازی که استفاده می‌کنی
python -m alembic upgrade head
```
**قبل از اجرا، migration رو بخون** — هیچ‌وقت کورکورانه اجرا نکن:
```bash
cat migrations/versions/<آخرین-revision>.py
```

### مرحله ۵: restart بات
اگه از systemd استفاده می‌کنی (احتمال زیاد):
```bash
systemctl restart khatmsaz
systemctl status khatmsaz   # برای اطمینان از اینکه بالا اومد
```

اگه از PM2 استفاده می‌کنی:
```bash
pm2 restart khatmsaz
pm2 logs khatmsaz --lines 50
```

اگه با screen یا tmux مستقیم اجرا می‌کنی:
```bash
# پیدا کردن PID
ps aux | grep "khatmsaz.bootstrap"
# kill کردن
kill <PID>
# دوباره start
source .venv/bin/activate
nohup python -m khatmsaz.bootstrap >> bot.log 2>&1 &
```

### مرحله ۶: چک کردن log
```bash
# systemd:
journalctl -u khatmsaz -n 100 -f

# فایل log مستقیم:
tail -f bot.log
```

---

## ۴. چک کردن سلامت بعد از deploy

۱. به بات پیام بده (یه `/start` ساده)
۲. چک کن log هیچ ERROR نداشته باشه
۳. اگه migration اجرا کردی، admin panel رو هم چک کن

---

## ۵. rollback اضطراری

اگه بعد از deploy چیزی خراب شد:

```bash
# روی سرور:
git log --oneline -5    # ببین commit قبلی چی بود
git checkout <commit-hash-قبلی>   # موقت
# یا:
git revert HEAD         # commit جدید که تغییر رو برمی‌گردونه
python -m alembic downgrade -1   # migration رو برگردون (اگه migration داشتی)
systemctl restart khatmsaz
```

---

## نکات مهم برای AI‌ها

- **هیچ‌وقت** بدون تأیید مالک push نکن
- **هیچ‌وقت** migration رو قبل از بررسی اجرا نکن
- اگه تست fail شد، deploy نکن — اول debug کن
- اگه migration شامل `DROP TABLE` یا `DROP COLUMN` هست، حتماً از مالک تأیید بگیر
- `.env` روی سرور فرق داره — قبل از هر deploy بپرس آیا باید `.env` هم آپدیت بشه
