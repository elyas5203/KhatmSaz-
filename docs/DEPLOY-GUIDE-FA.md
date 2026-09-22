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

## مرحله ۳ — انتقال فایل‌های پروژه به سرور (روش گیت‌هاب — توصیه‌شده)

به‌روزرسانی ۲۰۲۶-۰۹-۲۲: به‌جای فرستادن فایل با SFTP/SCP (که برای هر آپدیت
بعدی باید دوباره کل پروژه رو بفرستید)، از گیت‌هاب استفاده کنید — هر آپدیت
بعدی فقط با یک دستور (`git pull`) روی سرور انجام می‌شه. پوشه‌های حجیم و
غیرلازم (مثل `.venv`) و فایل `.env` (رمزها) خودکار از این انتقال کنار
گذاشته می‌شن — نیازی نیست دستی چیزی رو پاک کنید.

**روی کامپیوتر خودتون (این بخش رو من از قبل انجام دادم — پروژه الان یک
گیت محلی داره و اولین commit ثبت شده):**

1. برید به [github.com](https://github.com) و وارد اکانتتون بشید (یا
   یکی بسازید، رایگانه).
2. بالا سمت راست، روی علامت **+** بزنید → **New repository**.
3. یک اسم بذارید (مثلاً `khatmsaz`)، حتماً گزینهٔ **Private** رو انتخاب
   کنید (چون کد شامل ساختار پروژه‌ست، بهتره خصوصی بمونه)، و **هیچ‌کدوم**
   از گزینه‌های «Add a README»، «.gitignore»، «license» رو تیک نزنید
   (چون پروژه از قبل این‌ها رو داره). بعد **Create repository** رو بزنید.
4. صفحه‌ای باز می‌شه با چند دستور — فقط به آدرس بالای صفحه نیاز دارید،
   شبیه: `https://github.com/YOUR_USERNAME/khatmsaz.git`
5. تو ترمینال کامپیوتر خودتون (همون‌جایی که این دستورها قبلاً اجرا شده):
   ```bash
   cd C:\xampp\htdocs\Khatm
   git remote add origin https://github.com/YOUR_USERNAME/khatmsaz.git
   git branch -M main
   git push -u origin main
   ```
   به‌جای `YOUR_USERNAME` یوزرنیم گیت‌هاب خودتون رو بذارید.
6. اگه گیت‌هاب رمز عادی قبول نکرد (این روزها معمولاً قبول نمی‌کنه)، باید
   یک **Personal Access Token** بسازید: تو گیت‌هاب برید به
   Settings (روی عکس پروفایل بالا راست) → پایین صفحه **Developer settings**
   → **Personal access tokens** → **Tokens (classic)** → **Generate new token
   (classic)** → دسترسی `repo` رو تیک بزنید → **Generate token**. این
   توکن رو کپی کنید (فقط یک‌بار نشونش می‌ده) و موقع `git push` که رمز
   می‌خواد، به‌جای رمز همین توکن رو پیست کنید.

**روی سرور (داخل SSH):**

```bash
cd /root
git clone https://github.com/YOUR_USERNAME/khatmsaz.git
cd khatmsaz
```

موقع کلون کردن یک ریپازیتوری خصوصی، یوزرنیم و همون Personal Access Token
رو به‌جای رمز وارد کنید.

از این به بعد، مسیر پروژه روی سرور `/root/khatmsaz` است — دقیقاً مثل
حالتی که با SCP فرستاده می‌شد، بقیهٔ راهنما بدون تغییر ادامه پیدا می‌کنه.

> **آپدیت بعدی کد:** هر وقت من (هوش مصنوعی کدنویس) تغییری روی پروژهٔ
> شما دادم، فقط کافیه: از کامپیوتر خودتون `git push` بزنید (اگه من قبلاً
> commit نکرده باشم، بگید تا انجام بدم)، بعد رو سرور:
> ```bash
> cd /root/khatmsaz
> git pull
> source .venv/bin/activate
> pip install -r requirements.txt
> PYTHONPATH=src python -m alembic upgrade head
> systemctl restart khatmsaz
> ```

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

## مرحله ۱۱ — دامنه، HTTPS، و آدرس callback درگاه پرداخت

این مرحله لازمه چون درگاه پرداخت (پی‌پینگ) و مینی‌اپ تلگرام فقط با آدرس
HTTPS واقعی کار می‌کنن، نه با آی‌پی خام.

1. مطمئن بشید دامنهٔ `api.khatmsaz.com` به آی‌پی همین سرور اشاره می‌کنه
   (این کار قبلاً با تیم پشتیبانی هاست هماهنگ شده). از کامپیوتر خودتون
   می‌تونید چک کنید:
   ```bash
   nslookup api.khatmsaz.com
   ```
   باید همون آی‌پی سرور شما (91.107.137.22) رو نشون بده.

2. نصب Nginx و Certbot روی سرور:
   ```bash
   apt install -y nginx certbot python3-certbot-nginx
   ```

3. ساخت فایل تنظیمات Nginx:
   ```bash
   nano /etc/nginx/sites-available/khatmsaz
   ```
   این متن رو داخلش بذارید:
   ```nginx
   server {
       listen 80;
       server_name api.khatmsaz.com;
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```
   ذخیره کنید (`Ctrl+O`, `Enter`, `Ctrl+X`)، بعد:
   ```bash
   ln -s /etc/nginx/sites-available/khatmsaz /etc/nginx/sites-enabled/khatmsaz
   nginx -t
   systemctl reload nginx
   ```

4. فعال‌کردن HTTPS واقعی (رایگان، از Let's Encrypt):
   ```bash
   certbot --nginx -d api.khatmsaz.com
   ```
   یک ایمیل می‌خواد (برای یادآوری تمدید گواهی)، قوانین رو قبول کنید،
   و گزینهٔ Redirect از HTTP به HTTPS رو انتخاب کنید.

5. تست نهایی:
   ```bash
   curl -i https://api.khatmsaz.com/health
   ```
   باید ببینید: `{"status":"ok","database":"ok"}`

6. در `.env` سرور، این دو مقدار باید دقیقاً این‌طور باشن (نه `khatmsaz.com`
   ساده — طبق تیکت پشتیبانی #3122، دامنهٔ واقعی بات `api.khatmsaz.com`ه):
   ```
   PAYPING_CALLBACK_URL=https://api.khatmsaz.com/payments/payping/callback
   ADMIN_WEB_BASE_URL=https://api.khatmsaz.com
   PUBLIC_WEB_BASE_URL=https://api.khatmsaz.com
   ```
   بعد از تغییر:
   ```bash
   systemctl restart khatmsaz
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
