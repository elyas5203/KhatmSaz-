# راهنمای راه‌اندازی ختم‌ساز روی سرور (قدم به قدم، بدون نیاز به دانش برنامه‌نویسی)

این راهنما فرض می‌کنه شما:
- یک سرور (VPS) با اوبونتو ۲۲.۰۴ یا ۲۴.۰۴ دارید (هر شرکتی — آرشین، هتزنر، هر جای دیگه).
- به سرور با یک برنامه SSH وصل می‌شید. روی ویندوز ساده‌ترین راه **Windows Terminal** یا
  همون خط فرمانی هست که PowerShell/CMD نام داره؛ کافیه بنویسید:
  ```
  ssh root@IP_SERVER
  ```
  به‌جای `IP_SERVER` آی‌پی سرورتون رو بذارید و رمز عبوری که از شرکت سرور گرفتید رو وارد کنید.

هر دستوری که تو این راهنما می‌بینید رو **کپی کنید و داخل همون پنجره SSH که به سرور وصلید
پیست کنید و Enter بزنید.** به همین سادگی.

---

## مرحله ۱ — نصب پیش‌نیازها روی سرور

این دستورات رو یکی‌یکی (یا همه با هم، پشت سر هم) اجرا کنید:

```bash
apt update && apt upgrade -y
apt install -y python3 python3-venv python3-pip postgresql postgresql-contrib redis-server git
```

چند دقیقه طول می‌کشه. صبر کنید تا تموم بشه.

---

## مرحله ۲ — ساخت دیتابیس

```bash
sudo -u postgres psql -c "CREATE USER khatmsaz WITH PASSWORD 'یک-رمز-قوی-اینجا-بذارید';"
sudo -u postgres psql -c "CREATE DATABASE khatmsaz OWNER khatmsaz;"
```

⚠️ به‌جای `یک-رمز-قوی-اینجا-بذارید` یک رمز واقعی و قوی بذارید و **جایی یادداشتش کنید** —
چند خط پایین‌تر دوباره لازمش دارید.

---

## مرحله ۳ — انتقال فایل‌های پروژه به سرور

از روی کامپیوتر خودتون (نه داخل سرور)، یک پنجره جدید Windows Terminal باز کنید و این رو
اجرا کنید (مسیر `C:\xampp\htdocs\Khatm` رو با مسیر واقعی پروژه عوض نکنید، همینه):

```bash
scp -r "C:\xampp\htdocs\Khatm" root@IP_SERVER:/root/khatmsaz
```

به‌جای `IP_SERVER` آی‌پی سرورتون رو بذارید. این کار همه فایل‌ها رو می‌فرسته روی سرور، تو
پوشه `/root/khatmsaz`.

> اگه بعداً کد آپدیت شد، دوباره همین دستور رو اجرا کنید تا نسخه جدید جایگزین بشه (یا از Git
> استفاده کنید — این بخش رو بعداً با کمک هوش مصنوعی کدنویس می‌تونیم راه‌اندازی کنیم).

---

## مرحله ۴ — نصب برنامه روی سرور

برگردید به پنجره‌ای که به سرور وصله (همون SSH) و این‌ها رو اجرا کنید:

```bash
cd /root/khatmsaz
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## مرحله ۵ — گرفتن توکن بات تلگرام

1. توی تلگرام دنبال اکانت **@BotFather** بگردید و باهاش چت رو باز کنید.
2. پیام `/newbot` رو بفرستید.
3. یک اسم برای بات انتخاب کنید (مثلاً «ختم‌ساز»).
4. یک یوزرنیم برای بات انتخاب کنید — باید به `bot` ختم بشه (مثلاً `Khatm_Saz_bot`).
5. BotFather یک **توکن** بهتون می‌ده، یک رشته طولانی شبیه این:
   `123456789:AAExampleTokenHere`
   این توکن رو کپی کنید و جایی امن نگه دارید — این عملاً «کلید» بات شماست، **به هیچ‌کس
   ندید.**

---

## مرحله ۶ — گرفتن توکن بات بله

1. توی بله دنبال ربات‌ساز بله (Bale Bot Platform) بگردید — از داخل بله می‌تونید سرچ کنید
   یا از سایت رسمی بله دنبال بخش «ربات‌ساز» بگردید.
2. یک بات جدید بسازید (مشابه بات‌فادر تلگرام).
3. یک توکن مشابه بالا بهتون داده می‌شه — همون‌طور امن نگهش دارید.

> اگه لینک دقیق ربات‌ساز بله رو پیدا نکردید، به من (هوش مصنوعی کدنویس) بگید تا با هم دقیق
> پیداش کنیم؛ حدس نمی‌زنم.

---

## مرحله ۷ — ساخت فایل تنظیمات (.env)

داخل پنجره SSH که به سرور وصلید:

```bash
cd /root/khatmsaz
cp .env.example .env
nano .env
```

یک صفحه ویرایش متن باز می‌شه. این مقادیر رو پیدا کنید و پر کنید:

- `DATABASE_URL` رو این‌طوری عوض کنید (رمزی که مرحله ۲ ساختید رو جای `یک-رمز-قوی-اینجا-بذارید` بذارید):
  ```
  DATABASE_URL=postgresql+asyncpg://khatmsaz:یک-رمز-قوی-اینجا-بذارید@localhost:5432/khatmsaz
  ```
- `TELEGRAM_BOT_TOKEN=` → توکن مرحله ۵ رو جلوش بذارید.
- `TELEGRAM_BOT_USERNAME=` → یوزرنیم بات تلگرام (بدون @).
- `BALE_BOT_TOKEN=` → توکن مرحله ۶ رو جلوش بذارید.
- `OTP_HMAC_SECRET=` → یک رشته تصادفی امن. برای ساختنش این دستور رو تو یک پنجره دیگه اجرا کنید:
  ```bash
  python3 -c "import secrets; print(secrets.token_hex(32))"
  ```
  خروجیش رو کپی و جلوی `OTP_HMAC_SECRET=` بذارید.
- برای پیامک واقعی کاوه‌نگار این سه مقدار را از پنل بردارید و وارد کنید:
  ```
  SMS_PROVIDER=kavenegar
  SMS_API_KEY=کلید-وب‌سرویس-کاوه‌نگار
  SMS_SENDER=شماره-خط-خدماتی-تأییدشده
  ```
  نام کاربری یا رمز ورود پنل را داخل `.env` نگذارید. `DEV_OTP` در سرور
  واقعی حتماً `0` بماند. آدرس `SMS_API_BASE_URL` را معمولاً تغییر ندهید.

برای ذخیره و خروج از nano: کلید `Ctrl+O` بعد `Enter` بعد `Ctrl+X`.

---

## مرحله ۸ — ساخت جدول‌های دیتابیس

```bash
cd /root/khatmsaz
source .venv/bin/activate
PYTHONPATH=src python -m alembic upgrade head
```

اگه پیام‌های سبزرنگ/آبی دیدید و خطای قرمز نبود، یعنی موفق بوده.

---

## مرحله ۹ — تست دستی بات (قبل از دائمی کردنش)

```bash
cd /root/khatmsaz
source .venv/bin/activate
PYTHONPATH=src python -m khatmsaz.bootstrap
```

حالا برید تو تلگرام سراغ باتی که ساختید و `/start` رو بزنید — باید پیام خوش‌آمدگویی
بگیرید. همین کارو تو بله هم امتحان کنید.

اگه جواب گرفتید، عالیه ✅. برای متوقف کردن این تست موقت، `Ctrl+C` بزنید.

---

## مرحله ۱۰ — همیشه روشن نگه داشتن بات (systemd service)

این کار باعث می‌شه بات همیشه در پس‌زمینه اجرا باشه و اگه سرور ری‌استارت شد یا بات کرش کرد،
خودش دوباره بالا بیاد.

```bash
nano /etc/systemd/system/khatmsaz.service
```

این محتوا رو داخلش بذارید:

```ini
[Unit]
Description=KhatmSaz Bot
After=network.target postgresql.service redis-server.service

[Service]
Type=simple
WorkingDirectory=/root/khatmsaz
Environment=PYTHONPATH=/root/khatmsaz/src
ExecStart=/root/khatmsaz/.venv/bin/python -m khatmsaz.bootstrap
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

ذخیره کنید (`Ctrl+O`، `Enter`، `Ctrl+X`) و بعد:

```bash
systemctl daemon-reload
systemctl enable khatmsaz
systemctl start khatmsaz
```

---

## دستورات روزمره‌ای که لازمتون می‌شه

بررسی اینکه بات روشنه:
```bash
systemctl status khatmsaz
```

دیدن لاگ‌های زنده (برای دیباگ):
```bash
journalctl -u khatmsaz -f
```
(برای خروج از این حالت: `Ctrl+C`)

ری‌استارت کردن بات (بعد از هر تغییر کد):
```bash
systemctl restart khatmsaz
```

متوقف کردن بات:
```bash
systemctl stop khatmsaz
```

---

## اگه بات جواب نداد

1. `systemctl status khatmsaz` رو بزنید — اگه نوشته `active (running)` یعنی روشنه.
2. `journalctl -u khatmsaz -n 50` بزنید تا ۵۰ خط آخر لاگ رو ببینید — معمولاً خطا همونجا
   نوشته شده.
3. مطمئن شید `.env` توکن درست داره (بدون فاصله اضافه، بدون گیومه اضافه).
4. مطمئن شید دیتابیس روشنه: `systemctl status postgresql`.

اگه هر کدوم از این مراحل جواب نداد یا خطای عجیب دیدید، متن کامل خطا رو برای من (هوش
مصنوعی کدنویس) بفرستید — نه فقط بگید «کار نکرد»، چون بدون متن خطا نمی‌تونم دقیق تشخیص بدم
مشکل کجاست.

---

## نکته امنیتی مهم

فایل `.env` شامل توکن‌ها و رمز دیتابیس شماست — **هیچ‌وقت این فایل رو جایی پابلیک (مثل یک
چت عمومی یا گیت‌هاب پابلیک) آپلود نکنید.** اگه فکر می‌کنید یکی از توکن‌ها لو رفته، همون بات
رو تو BotFather/ربات‌ساز بله عوض کنید (revoke/regenerate token) و `.env` رو با توکن جدید
آپدیت کنید، بعد `systemctl restart khatmsaz`.
