"""Central translation registry for the bot's user-facing text.

<b>Why this exists (owner request, 2026-09-20):</b> the bot must become fully
multi-language (fa/ar/en) — buttons, menus, help text, everything — not
just the reminder templates that already had per-locale rows in the
`message_template` module.

**The one non-obvious architectural constraint every future contributor
must know:** aiogram's `@router.message(F.text == SOME_CONSTANT)` filters
run *before* any handler code executes, so they cannot look up "this
user's language" from the database first. A reply-keyboard button whose
label changes per language therefore cannot be matched with a single
`F.text == X` filter anymore — it must be matched against the set of *all*
language variants of that button. This module's `variants(key)` gives you
exactly that set; see `bot/keyboards.py`'s `*_BUTTON_TEXTS` frozensets and
every `F.text.in_(...)` filter in `bot/handlers/*.py` for the pattern.

<b>How to add a new translated string:</b>
1. Pick a short dotted key, grouped by feature area (e.g. `"menu.create"`,
   `"settings.home.title"`).
2. Add it to `_STRINGS` below with all three languages. Never omit `fa` —
   it is the fallback if a translation is missing for another language.
3. Call `t(key, lang)` wherever you used to hardcode the Persian string.
4. If the string is a reply-keyboard button label matched by
   `F.text == ...` anywhere, use `variants(key)` + `F.text.in_(...)`
   instead — see the constraint above.

<b>Where the user's language actually lives:</b> `UserSettings.language`
(module `settings`, already existed before this — `settings_service.set_language`,
`SUPPORTED_LANGUAGES`). This module does not store or fetch it; callers
pass whatever language string they already loaded from a session.
"""

SUPPORTED_LANGUAGES = ("fa", "ar", "en")
_DEFAULT_LANGUAGE = "fa"

# key -> {lang: text}. Keep `fa` first and always present.
_STRINGS: dict[str, dict[str, str]] = {
    "share.pages": {"fa": "📖 سهم شما از «{title}»: صفحات {pages}", "ar": "📖 حصتك من «{title}»: الصفحات {pages}", "en": "📖 Your share in “{title}”: pages {pages}"},
    "share.amount": {"fa": "🌱 سهم شما از «{title}»: {amount}", "ar": "🌱 حصتك من «{title}»: {amount}", "en": "🌱 Your share in “{title}”: {amount}"},
    "share.followup": {"fa": "⏳ دو ساعت از دریافت این سهم گذشته است. پس از خواندن، انجامش را ثبت کنید؛ تعهد شما تا انجام باقی می‌ماند.", "ar": "⏳ مضت ساعتان على استلام هذه الحصة. سجّل إتمامها بعد القراءة؛ يبقى الالتزام حتى إتمامها.", "en": "⏳ You received this share two hours ago. Confirm it after reading; your commitment remains until completed."},
    "share.deadline": {"fa": "⏰ کمتر از یک ساعت تا پایان زمان امروز مانده است. لطفاً سهمتان را بخوانید و ثبت کنید تا تعهد انجام‌نشده‌ای باقی نماند.", "ar": "⏰ بقي أقل من ساعة على نهاية وقت اليوم. يرجى قراءة حصتك وتسجيلها كي لا يبقى الالتزام غير مكتمل.", "en": "⏰ Less than an hour remains before today’s deadline. Please read and confirm your share; unfinished commitments remain due."},
    "commit.ask_count.quran": {
        "fa": "چند صفحه می‌خواهید یک‌جا دریافت کنید؟",
        "ar": "كم صفحة تريد استلامها في هذه الحصة؟",
        "en": "How many pages would you like in this share?",
    },
    "commit.ask_times_per_period.quran": {
        "fa": "در هر روز انتخاب‌شده چند صفحه بخوانید؟",
        "ar": "كم صفحة تقرأ في كل يوم تختاره؟",
        "en": "How many pages on each selected day?",
    },

    "create_khatm.ask_daily_quran": {
        "fa": "سهم روزانهٔ هر عضو چند صفحه باشد؟ مثلاً ۲ صفحه.",
        "ar": "كم صفحة يقرأ كل عضو يومياً؟ مثلاً صفحتان.",
        "en": "How many pages daily? (e.g. 2)"
    },
    "create_khatm.ask_daily_salawat": {
        "fa": "سهم روزانهٔ هر عضو چند صلوات باشد؟ مثلاً ۱۰۰ صلوات.",
        "ar": "كم صلاة على النبي لكل عضو يومياً؟ مثلاً 100.",
        "en": "How many salawat daily? (e.g. 100)"
    },
    "create_khatm.ask_daily_laan": {
        "fa": "هر عضو ذکر تعیین‌شده را روزانه چند بار بخواند؟ مثلاً ۵۰ بار.",
        "ar": "كم مرة يقرأ كل عضو الذكر المحدد يومياً؟ مثلاً 50.",
        "en": "How many la'n daily? (e.g. 50)"
    },
    "create_khatm.ask_daily_dua": {
        "fa": "هر عضو دعا یا زیارت را روزانه چند بار بخواند؟ مثلاً یک بار.",
        "ar": "كم مرة يقرأ كل عضو الدعاء أو الزيارة يومياً؟ مثلاً مرة واحدة.",
        "en": "How many times daily? (e.g. 1)"
    },
    "days.monday": {"fa": "دوشنبه", "ar": "الاثنين", "en": "Mon"},
    "days.tuesday": {"fa": "سه‌شنبه", "ar": "الثلاثاء", "en": "Tue"},
    "days.wednesday": {"fa": "چهارشنبه", "ar": "الأربعاء", "en": "Wed"},
    "days.thursday": {"fa": "پنج‌شنبه", "ar": "الخميس", "en": "Thu"},
    "days.friday": {"fa": "جمعه", "ar": "الجمعة", "en": "Fri"},
    "days.saturday": {"fa": "شنبه", "ar": "السبت", "en": "Sat"},
    "days.sunday": {"fa": "یکشنبه", "ar": "الأحد", "en": "Sun"},


    "commit.regular_saved_detailed": {
        "fa": "✅ برنامه شما ذخیره شد:\n\n📅 روزها: {days_text}\n⏰ ساعت یادآوری: {hour}\n📖 مقدار هر نوبت: {times} {unit}\n📊 مجموع در هفته: {weekly_sum} {unit}\n\nسر وقت تعیین‌شده، محتوا برای شما ارسال می‌شود.",
        "ar": "✅ تم حفظ جدولك:\n\n📅 الأيام: {days_text}\n⏰ وقت التذكير: {hour}\n📖 الكمية لكل مرة: {times} {unit}\n📊 المجموع الأسبوعي: {weekly_sum} {unit}\n\nسيتم إرسال المحتوى لك في الوقت المحدد.",
        "en": "✅ Your schedule is saved:\n\n📅 Days: {days_text}\n⏰ Reminder Time: {hour}\n📖 Amount per turn: {times} {unit}\n📊 Weekly Total: {weekly_sum} {unit}\n\nContent will be sent at the specified time."
    },
    "commit.every_day": {
        "fa": "هر روز",
        "ar": "كل يوم",
        "en": "Every day"
    },
    "commit.unit.salawat": {"fa": "صلوات", "ar": "صلوات", "en": "Salawat"},
    "commit.unit.dua": {"fa": "مرتبه", "ar": "مرة", "en": "times"},


    "portions.open_reservation_warning": {
        "fa": "شما از قبل {count} سهم رزرو شده دارید. مهلت آن رو به اتمام است.",
        "ar": "لديك {count} مشاركة محجوزة. مهلتها توشك على الانتهاء.",
        "en": "You have a reserved contribution of {count}. The deadline is approaching."
    },
    "portions.open_capacity_full": {
        "fa": "ظرفیت این ختم تکمیل شده است. از مشارکت شما متشکریم.",
        "ar": "اكتملت سعة هذه الختمة. شكرًا لمشاركتك.",
        "en": "This khatm's capacity is full. Thank you for participating."
    },
    "portions.open_already_reserved": {
        "fa": "شما از قبل یک مشارکت در حال انجام دارید. لطفاً ابتدا آن را به پایان برسانید.",
        "ar": "لديك بالفعل مشاركة قيد الإنجاز. يرجى إكمالها أولاً.",
        "en": "You already have an active reservation. Please complete it first."
    },
    "portions.open_reserved_success": {
        "fa": "شما {count} {unit} رزرو کردید.",
        "ar": "لقد قمت بحجز {count} {unit}.",
        "en": "You have reserved {count} {unit}."
    },
    "portions.open_reserved_deadline": {
        "fa": "لطفاً پس از انجام، با فشردن دکمه زیر آن را ثبت کنید. (مهلت: ۷ روز)",
        "ar": "يرجى تسجيله بالضغط على الزر أدناه بعد الانتهاء. (المهلة: 7 أيام)",
        "en": "Please tap the button below once you complete it. (Deadline: 7 days)"
    },
    "portions.button.complete_reservation": {
        "fa": "انجام شد",
        "ar": "تم الإنجاز",
        "en": "Completed"
    },

    "menu.today": {
        "fa": "📖 انجام قرائت امروز",
        "ar": "📖 إنجاز قراءة اليوم",
        "en": "📖 Complete today's reading",
    },
    "menu.my_khatms": {"fa": "🕋 لیست ختم‌های من", "ar": "🕋 قائمة ختماتي", "en": "🕋 My Khatms List"},
    "menu.report": {"fa": "📈 گزارش عملکرد من", "ar": "📈 تقرير أدائي", "en": "📈 My Performance"},
    "menu.settings": {"fa": "⚙️ تنظیمات حساب", "ar": "⚙️ إعدادات الحساب", "en": "⚙️ Account Settings"},
    "menu.create": {"fa": "➕ ساخت ختم جدید", "ar": "➕ إنشاء ختمة جديدة", "en": "➕ Create New Khatm"},
    "menu.help": {"fa": "❓ راهنمای کامل", "ar": "❓ دليل كامل", "en": "❓ Full Guide"},

    # New Parent Menus
    "menu.creator.management": {"fa": "👑 مدیریت ختم‌ها", "ar": "👑 إدارة الختمات", "en": "👑 Khatm Management"},
    "menu.creator.finance": {"fa": "📊 گزارش و مالی", "ar": "📊 التقارير والمالية", "en": "📊 Report & Finance"},
    "menu.creator.support": {"fa": "❓ راهنما و پشتیبانی", "ar": "❓ الدعم والدليل", "en": "❓ Help & Support"},
    "menu.creator.wallet": {"fa": "💳 شارژ کیف پول", "ar": "💳 شحن المحفظة", "en": "💳 Top up Wallet"},
    "creator.finance.menu_intro": {
        "fa": "📊 گزارش و مالی\n\nبرای دیدن آمار ختم‌های ساخته‌شده، «گزارش عملکرد من» را بزنید. برای دیدن موجودی یا پرداخت، «شارژ کیف پول» را انتخاب کنید.",
        "ar": "📊 التقارير والمالية\n\nلعرض تقارير ختماتك اختر تقرير الأداء، ولعرض الرصيد أو الدفع اختر شحن المحفظة.",
        "en": "📊 Reports and finance\n\nChoose My Performance for your created khatms, or Top up Wallet to view your balance and pay.",
    },
    "report.creator_no_active_khatms": {
        "fa": "📈 گزارش ختم‌های شما\n\nدر حال حاضر ختم فعالِ ساخته‌شده‌ای ندارید. اگر ختمی ساخته‌اید که پایان یافته، از بخش «مدیریت ختم‌ها» آن را ببینید.",
        "ar": "📈 تقرير ختماتك\n\nلا توجد لديك حالياً ختمة نشطة أنشأتها.",
        "en": "📈 Your khatm report\n\nYou currently have no active khatm created by you.",
    },
    "menu.back_to_main": {"fa": "🔙 بازگشت به منوی اصلی", "ar": "🔙 العودة للقائمة الرئيسية", "en": "🔙 Back to Main Menu"},

    # Text for menus

    "welcome.text": {
        "fa": (
            "سلام! به <b>ختم‌ساز</b> خوش اومدی 🌱\n\n"
            "این بات مخصوص <b>ساختن ختم</b> است — همین‌جا می‌تونی ختم قرآن، صلوات، دعا یا زیارت گروهی بسازی "
            "و لینکش رو با دیگران به اشتراک بذاری.\n\n"
            "بیا همین حالا اولین ختمت رو بسازیم 👇"
        ),
        "ar": (
            "مرحباً بك في <b>ختم‌ساز</b> 🌱\n\n"
            "هذا البوت مخصّص <b>لإنشاء الختمات</b> — من هنا يمكنك إنشاء ختمة قرآن أو صلوات أو دعاء أو زيارة جماعية "
            "ومشاركة رابطها مع الآخرين.\n"
            "<i>للمشاركة</i> في ختمة، ادخل عبر رابط تلك الختمة إلى البوت الخاص بها (لا من هنا).\n\n"
            "لننشئ ختمتك الأولى الآن 👇"
        ),
        "en": (
            "Welcome to <b>KhatmSaz</b> 🌱\n\n"
            "This bot is for <b>creating Khatms</b> — build a group Quran, Salawat, Dua or Ziyarat Khatm here "
            "and share its link with others.\n"
            "To <i>take part</i> in a Khatm, open that Khatm's own link into its bot (not here).\n\n"
            "Let's create your first Khatm now 👇"
        ),
    },
    "navigation.cancelled": {
        "fa": "این مرحله لغو شد و به منوی اصلی برگشتید.",
        "ar": "تم إلغاء هذه الخطوة والعودة إلى القائمة الرئيسية.",
        "en": "This step was cancelled. You're back at the main menu.",
    },
    "navigation.interrupted": {
        "fa": "این مرحله لغو شد. حالا دوباره گزینهٔ موردنظرتون رو بزنید.",
        "ar": "تم إلغاء هذه الخطوة. اختر الخيار الذي تريده مرة أخرى.",
        "en": "This step was cancelled. Choose the option you want again.",
    },
    "navigation.admin_cancelled": {
        "fa": "این مرحله لغو شد. برای ورود به مدیریت /admin_web_login را بفرستید.",
        "ar": "تم إلغاء هذه الخطوة. أرسل /admin_web_login لفتح لوحة الإدارة.",
        "en": "This step was cancelled. Send /admin_web_login to open admin management.",
    },
    "navigation.admin_interrupted": {
        "fa": "این مرحله لغو شد. دستور مدیریتی موردنظرتون رو دوباره بفرستید؛ ورود پنل: /admin_web_login",
        "ar": "تم إلغاء هذه الخطوة. أرسل أمر الإدارة مرة أخرى؛ دخول اللوحة: /admin_web_login",
        "en": "This step was cancelled. Send the admin command again; panel login: /admin_web_login",
    },
    "language.prompt": {
        "fa": "زبان بات رو انتخاب کن:",
        "ar": "اختر لغة البوت:",
        "en": "Choose the bot's language:",
    },
    "language.saved": {
        "fa": "زبان روی فارسی تنظیم شد ✅",
        "ar": "تم ضبط اللغة على العربية ✅",
        "en": "Language set to English ✅",
    },
    "registration.ask_name": {
        "fa": "برای اینکه بتوانید در این ختم شرکت کنید، لازم است چند اطلاعات کوتاه را فقط یک‌بار وارد کنید. این اطلاعات برای ثبت سهم شما و گزارش درست ختم استفاده می‌شود 🌱\n\n❓ <b>سؤال ۱ از ۵</b>\nنام و نام خانوادگی‌تان را بنویسید:",
        "ar": "قبل الانضمام سنطرح عليك بعض الأسئلة القصيرة (مرة واحدة فقط) 🌱\n\nاكتب اسمك الكامل:",
        "en": "Before you join, we'll ask a few short questions (only once) 🌱\n\nPlease enter your full name:",
    },
    "registration.name_required": {
        "fa": "لطفاً نام و نام خانوادگیتون رو بنویسید.",
        "ar": "يرجى كتابة اسمك الكامل.",
        "en": "Please enter your full name.",
    },
    "registration.ask_phone": {
        "fa": "❓ <b>سؤال ۲ از ۵</b>\nشماره موبایلتان را با دکمه پایین به اشتراک بگذارید، یا بنویسید (مثلاً 09121234567):",
        "ar": "شارك رقم هاتفك بالزر أدناه، أو اكتبه مع رمز الدولة (مثلاً +989121234567):",
        "en": "Share your mobile number with the button below, or type it with the country code (for example +989121234567):",
    },
    "registration.ask_phone_share_only": {
        "fa": "❓ <b>سؤال ۲ از ۵</b>\nبرای ثبت شماره موبایلتان، دکمهٔ «{share_button}» زیر همین پیام را بزنید.",
        "ar": "لتسجيل رقم هاتفك، اضغط فقط زر «{share_button}» أسفل هذه الرسالة.",
        "en": "To register your mobile number, just tap the “{share_button}” button below this message.",
    },
    "registration.use_share_button_only": {
        "fa": "لطفاً شماره رو تایپ نکنید — فقط دکمهٔ «{share_button}» زیر رو بزنید.",
        "ar": "الرجاء عدم كتابة الرقم — فقط اضغط زر «{share_button}» أدناه.",
        "en": "Please don't type the number — just tap the “{share_button}” button below.",
    },
    "registration.share_phone": {
        "fa": "📱 اشتراک‌گذاری شماره من",
        "ar": "📱 مشاركة رقم هاتفي",
        "en": "📱 Share my phone number",
    },
    "registration.shared_phone_invalid": {
        "fa": "شمارهٔ اشتراک‌گذاری‌شده معتبر نیست؛ لطفاً شماره را با کد کشور بنویسید.",
        "ar": "الرقم المشارك غير صالح؛ اكتبه مع رمز الدولة.",
        "en": "The shared number is not valid. Please type it with the country code.",
    },
    "registration.phone_invalid": {
        "fa": "لطفاً یک شماره موبایل معتبر بنویسید یا از دکمه اشتراک‌گذاری استفاده کنید.",
        "ar": "اكتب رقم هاتف صالحاً أو استخدم زر المشاركة.",
        "en": "Please enter a valid mobile number or use the share button.",
    },
    "registration.phone_saved": {
        "fa": "✅ شماره ثبت شد.",
        "ar": "✅ تم حفظ الرقم.",
        "en": "✅ Phone number saved.",
    },
    "registration.ask_province": {
        "fa": "❓ <b>سؤال ۳ از ۵</b>\nاستان محل زندگی‌تان را از فهرست زیر انتخاب کنید:",
        "ar": "اختر محافظة إقامتك من القائمة أدناه:",
        "en": "Choose the province where you live from the list below:",
    },
    "registration.outside_iran": {
        "fa": "خارج از ایران",
        "ar": "خارج إيران",
        "en": "Outside Iran",
    },
    "registration.ask_city": {
        "fa": "❓ <b>سؤال ۴ از ۵</b>\nنام شهرتان را بنویسید (مثلاً «مشهد» یا «اصفهان»):",
        "ar": "اكتب اسم مدينتك:",
        "en": "Enter the name of your city:",
    },
    "registration.city_required": {
        "fa": "لطفاً نام شهرتون رو بنویسید.",
        "ar": "يرجى كتابة اسم مدينتك.",
        "en": "Please enter your city name.",
    },
    "registration.ask_gender": {
        "fa": "❓ <b>سؤال ۵ از ۵</b>\nجنسیتتان را انتخاب کنید (فقط برای گزارش‌های آماری ختم استفاده می‌شود):",
        "ar": "اختر الجنس (يُستخدم فقط في الإحصاءات العامة للختمة):",
        "en": "Select your gender (used only for aggregate khatm statistics):",
    },
    "registration.gender_male": {"fa": "مرد", "ar": "رجل", "en": "Male"},
    "registration.gender_female": {"fa": "زن", "ar": "امرأة", "en": "Female"},
    "registration.completed": {
        "fa": "ثبت‌نام شما کامل شد ✅ از این به بعد دیگر نیازی به تکرار این مراحل نیست.\nاز منوی پایین می‌تونید یک ختم بسازید یا با لینک دعوت به ختم دیگران بپیوندید.",
        "ar": "اكتمل تسجيلك ✅ لن تحتاج إلى تكرار هذه الخطوات.\nيمكنك الآن إنشاء ختمة من القائمة أو الانضمام إلى ختمة عبر رابط دعوة.",
        "en": "Your registration is complete ✅ You won't need to repeat these steps.\nYou can now create a khatm from the menu or join one through an invite link.",
    },
    "profile.ask_name": {
        "fa": "برای ویرایش پروفایل، نام و نام خانوادگیتون رو بنویسید:",
        "ar": "لتعديل ملفك الشخصي، اكتب اسمك الكامل:",
        "en": "To edit your profile, enter your full name:",
    },
    "profile.ask_phone": {
        "fa": "شماره موبایلتون رو بنویسید یا با دکمه پایین به اشتراک بذارید:",
        "ar": "اكتب رقم هاتفك أو شاركه باستخدام الزر أدناه:",
        "en": "Enter your mobile number or share it with the button below:",
    },
    "profile.verified_phone_locked": {
        "fa": "شمارهٔ فعلی شما تأیید شده است و از ویرایش عادی پروفایل عوض نمی‌شود. برای حفظ امنیت و همهٔ سوابق، دستور /change_phone را بزنید تا رمز به شمارهٔ جدید ارسال شود.",
        "ar": "رقمك الحالي موثّق ولا يمكن تغييره من تعديل الملف العادي. لحماية حسابك وسجلاتك، أرسل /change_phone ليتم إرسال رمز إلى الرقم الجديد.",
        "en": "Your current number is verified and cannot be changed through normal profile editing. To protect your account and history, send /change_phone and a code will be sent to the new number.",
    },
    "profile.user_not_found": {
        "fa": "حساب کاربری پیدا نشد.",
        "ar": "لم يتم العثور على حساب المستخدم.",
        "en": "User account not found.",
    },
    "profile.updated": {
        "fa": "پروفایلتون با موفقیت به‌روزرسانی شد ✅",
        "ar": "تم تحديث ملفك الشخصي بنجاح ✅",
        "en": "Your profile was updated successfully ✅",
    },
    "help.home": {
        "fa": "📖 <b>راهنمای ختم‌ساز</b>\n\nلازم نیست دستوری حفظ کنید؛ موضوع موردنظرتان را از دکمه‌های زیر انتخاب کنید.\n\nختم می‌تواند «تعهدی» باشد؛ یعنی سهم پذیرفته‌شده باید انجام شود، یا «آزاد» باشد؛ یعنی هرکس بدون تعهد هر مقدار که خواست مشارکت می‌کند. عمومی یا خصوصی بودن فقط روش ورود اعضا را مشخص می‌کند.\n\nبرای دریافت زودتر سهم همان روز، «📖 انجام قرائت امروز» را بزنید.",
        "ar": "❓ دليل ختم‌ساز\n\nلا تحتاج إلى حفظ الأوامر. اختر الموضوع المطلوب من الأزرار أدناه؛ كل قسم مشروح خطوة بخطوة.\n\nلقراءة حصة اليوم مبكراً اضغط «📖 إنجاز قراءة اليوم» من القائمة السفلية.",
        "en": "❓ KhatmSaz Guide\n\nYou do not need to memorize commands. Choose a topic with the buttons below; every section is explained step by step.\n\nTo read today's portion early, tap “📖 Complete today's reading” in the bottom menu.",
    },
    "help.join": {
        "fa": "👋 شروع و عضویت در یک ختم\n\n۱) لینکی را که سازنده برایتان فرستاده باز کنید.\n۲) اگر اولین بار است، بات نام، شماره موبایل، استان، شهر و جنسیت را مرحله‌به‌مرحله می‌پرسد.\n۳) تنظیم‌های همان ختم را روی یک پیام انتخاب می‌کنید و عضویتتان کامل می‌شود.\n۴) اگر ختم خصوصی باشد، درخواست برای سازنده می‌رود و بعد از تأیید به شما خبر داده می‌شود.\n\nبعد از عضویت، از «📖 انجام قرائت امروز» یک ختم را انتخاب کنید تا سهم همان روز زودتر برایتان فرستاده شود.",
        "ar": "👋 البدء والانضمام إلى ختمة\n\n١) افتح الرابط الذي أرسله منشئ الختمة.\n٢) سترى التفاصيل أولاً؛ فتح الرابط وحده لا يعني أنك انضممت.\n٣) اضغط زر الانضمام. في المرة الأولى يسألك البوت عن الاسم والهاتف والمحافظة والمدينة والجنس خطوة بخطوة.\n٤) في الختمة الملتزمة، اقرأ التعهد القصير ولا تؤكده إلا إذا قبلته.\n٥) إذا كانت الختمة خاصة، ينتظر طلبك موافقة المنشئ وسيصلك إشعار بعدها.\n\nبعد الانضمام تجد حصصك دائماً في «📖 إنجاز قراءة اليوم» و«🕋 ختماتي».",
        "en": "👋 Starting and joining a khatm\n\n1) Open the invite link sent by the creator.\n2) You first see the khatm details; opening the link alone does not join you.\n3) Tap the join button. On your first time, the bot asks for your name, phone, province, city, and gender step by step.\n4) For a commitment khatm, read the short pledge and confirm only if you accept it.\n5) For a private khatm, your request waits for the creator's approval and you are notified afterward.\n\nAfter joining, your portions are always available under “📖 Complete today's reading” and “🕋 My Khatms”.",
    },
    "help.portion": {
        "fa": "📖 دیدن و انجام سهم\n\n۱) در منوی پایین «📖 انجام قرائت امروز» را بزنید.\n۲) زیر سهم قرآن روی «📖 نمایش محتوای سهم» بزنید تا تصویر صفحه‌ها ارسال شود.\n۳) اگر صوت را روشن کرده باشید، تلاوت همان بازه هم می‌آید. بعضی فایل‌های کانال دو یا سه صفحه را یکجا دارند.\n۴) بعد از خواندن فقط یک بار «✅ انجام دادم» را بزنید؛ تأیید دوم لازم نیست.\n۵) اگر اشتباه زدید، تا پنج دقیقه می‌توانید آخرین ثبت را برگردانید.\n\nبرای ختم آزاد، مقدار انجام‌شده را وارد می‌کنید. در ختم تعهدی می‌توانید مقدار را یک‌جا یا چند مرحله ثبت کنید.",
        "ar": "📖 عرض الحصة وإتمامها\n\n١) اضغط «📖 إنجاز قراءة اليوم» في القائمة السفلية.\n٢) تحت حصة القرآن اضغط زر عرض المحتوى لتصلك صور الصفحات.\n٣) إذا فعّلت الصوت يصلك تلاوة النطاق نفسه؛ وقد يغطي ملف واحد صفحتين أو ثلاثاً.\n٤) بعد القراءة اضغط «✅ أنجزت» مرة واحدة فقط.\n٥) إذا ضغطت بالخطأ يمكنك التراجع عن آخر تسجيل خلال خمس دقائق.\n\nفي الختمة المفتوحة تُدخل الكمية المنجزة، وفي الملتزمة يمكنك تسجيلها دفعة واحدة أو على مراحل.",
        "en": "📖 Viewing and completing a portion\n\n1) Tap “📖 Complete today's reading” in the bottom menu.\n2) Under a Quran portion, tap the content button to receive the page images.\n3) If audio is enabled, the matching recitation is sent too; one channel file may cover two or three pages.\n4) After reading, tap “✅ Done” only once.\n5) If you tap by mistake, you can undo the latest completion for five minutes.\n\nFor an open khatm, enter the amount completed. For a commitment khatm, you may record it all at once or in several steps.",
    },
    "help.create": {
        "fa": "➕ ساخت یک ختم جدید\n\n۱) در بات ختم‌ساز «➕ ساخت ختم جدید» را بزنید و در صورت نیاز مشخصات و تأیید شماره را کامل کنید.\n۲) خانوادهٔ محتوا، آزاد یا تعهدی بودن و تنظیم‌های مرتبط را مرحله‌به‌مرحله انتخاب کنید. عنوان مناسب خودکار ساخته می‌شود و با «مرحلهٔ قبل» می‌توانید انتخاب‌ها را اصلاح کنید.\n۳) پیش از ساخت، خلاصه و هزینهٔ نهایی را می‌بینید؛ تا تأیید نهایی چیزی ساخته یا کم نمی‌شود.\n۴) بعد از ساخت، لینک اختصاصی را برای مخاطبانتان بفرستید.\n\nاگر دعای موردنظر در فهرست نیست، «درخواست نوع ختم جدید» را بزنید.",
        "ar": "➕ إنشاء ختمة جديدة\n\n١) في بوت ختم‌ساز اضغط إنشاء ختمة جديدة وأكمل البيانات وتوثيق الهاتف عند الحاجة.\n٢) اختر عائلة المحتوى ثم الوضع المفتوح أو الملتزم والإعدادات المرتبطة خطوة بخطوة. يُنشأ العنوان تلقائياً ويمكنك الرجوع لتعديل الاختيارات.\n٣) قبل الإنشاء ترى الملخص والتكلفة النهائية؛ لا يُنشأ أو يُخصم شيء قبل التأكيد.\n٤) بعد الإنشاء شارك رابطك الخاص مع جمهورك.\n\nإذا لم تجد الدعاء المطلوب فاستخدم زر طلب نوع جديد.",
        "en": "➕ Creating a new khatm\n\n1) In the KhatmSaz bot, tap Create New Khatm and complete profile or phone verification when requested.\n2) Choose the content family, open or commitment mode, and relevant settings step by step. A suitable title is created automatically, and Back lets you revise choices.\n3) Before creation you see the summary and final cost; nothing is created or charged before confirmation.\n4) After creation, share your private invite link with your audience.\n\nIf the desired dua is missing, use Request a New Khatm Type.",
    },
    "help.wallet": {
        "fa": "💳 کیف پول و پرداخت\n\n• «دیدن موجودی و شارژ» موجودی، اعتبار هدیه، پلن و مبلغ‌های قابل انتخاب را نشان می‌دهد.\n• «فاکتورها و رسیدهای من» آخرین خریدها و بازپرداخت‌ها را نشان می‌دهد.\n• هنگام ساخت ختم پولی، مبلغ نهایی قبل از تأیید نمایش داده می‌شود. اگر کد تخفیف ندارید مرحلهٔ اضافه‌ای لازم نیست.\n\nپرداخت فقط بعد از تأیید واقعی درگاه موفق است. اگر ختم پولی را پیش از ورود اولین عضو لغو کنید، مبلغ به کیف پول داخلی برمی‌گردد.",
        "ar": "💳 المحفظة والدفع\n\n• زر الرصيد والشحن يعرض الرصيد والهدية والخطة والمبالغ المتاحة.\n• زر الفواتير والإيصالات يعرض آخر المشتريات والاستردادات.\n• عند إنشاء ختمة مدفوعة تظهر التكلفة النهائية قبل التأكيد، ولا توجد خطوة إضافية إذا لم يكن لديك رمز خصم.\n\nلا ينجح الدفع إلا بعد تأكيد بوابة الدفع فعلياً. وإذا ألغيت ختمة مدفوعة قبل انضمام أول عضو يعود المبلغ إلى المحفظة الداخلية.",
        "en": "💳 Wallet and payments\n\n• The balance and top-up button shows your balance, gift credit, plan, and available amounts.\n• The invoices button shows recent purchases and refunds.\n• For a paid khatm, the final amount appears before confirmation; no extra step is required if you have no coupon.\n\nA payment succeeds only after the gateway verifies it. If a paid khatm is cancelled before the first member joins, the amount returns to the internal wallet.",
    },
    "help.settings": {
        "fa": "⚙️ تنظیمات شخصی\n\nاز این بخش می‌توانید زبان، ساعت یادآوری، منطقهٔ زمانی، پیامک، مشخصات، شماره و اتصال حساب قبلی را با دکمه مدیریت کنید. سازنده‌ها از همین صفحه به پنل سازنده هم می‌رسند.\n\nپیام‌های ضروریِ تعهد خاموش نمی‌شوند تا سهم پذیرفته‌شده فراموش نشود. تنظیم صوت قرآن داخل راهنمای محتوای سهم قرآن در دسترس است.",
        "ar": "⚙️ الإعدادات الشخصية\n\nمن هنا تدير اللغة ووقت التذكير والمنطقة الزمنية والرسائل والملف ورقم الهاتف وربط الحساب السابق بالأزرار. ويصل المنشئ أيضاً إلى لوحته من هذه الصفحة.\n\nلا تُعطّل رسائل الالتزام الضرورية. إعداد صوت القرآن متاح من دليل محتوى حصة القرآن.",
        "en": "⚙️ Personal settings\n\nUse buttons here to manage language, reminder time, timezone, SMS, profile, phone, and previous-account linking. Creators can also open their panel from this page.\n\nEssential commitment reminders stay enabled so accepted shares are not forgotten. Quran audio is available from the Quran portion-content guide.",
    },
    "help.manage": {
        "fa": "🧭 مدیریت ختمی که ساخته‌اید\n\n۱) «📊 پنل سازنده» را باز کنید؛ لینک دعوت، QR، آمار، اعضا، موارد نیازمند توجه و CSV آنجاست.\n۲) از «ختم‌های من» می‌توانید عنوان، خوش‌آمد، نمایش عمومی، پیام‌رسان‌های مجاز، لحن یادآوری، مهلت و افزایش امن هدف را ویرایش کنید. کاهش هدف و تغییر ساختار قرآن برای حفظ سابقه بسته است.\n۳) پیام گروهی متنی، عکس، فیلم یا ویس پس از تأیید محتوا ارسال می‌شود و می‌تواند بر اساس ختم، استان و جنسیت فیلتر شود.\n۴) لغو ختم پولی فقط پیش از ورود اولین عضو با بازپرداخت داخلی ممکن است.\n\nاطلاعات اعضا خصوصی است و فقط سازندهٔ همان ختم و مدیر مجاز آن را می‌بینند.",
        "ar": "🧭 إدارة ختمة أنشأتها\n\n١) افتح لوحة المنشئ للوصول إلى رابط الدعوة وQR والإحصاءات والأعضاء والتنبيهات وCSV.\n٢) من ختماتي يمكنك تعديل العنوان والترحيب والظهور والمنصات ونبرة التذكير والمهلة وزيادة الهدف بأمان. خفض الهدف وتغيير بنية القرآن مغلقان لحماية السجل.\n٣) تُرسل الرسائل النصية أو الصور أو الفيديو أو الصوت بعد مراجعة المحتوى، مع تصفية حسب الختمة والمحافظة والجنس.\n٤) استرداد إلغاء الختمة المدفوعة متاح فقط قبل انضمام أول عضو.\n\nبيانات الأعضاء خاصة بالمنشئ والمدير المصرح.",
        "en": "🧭 Managing a khatm you created\n\n1) Open the Creator Panel for the invite link, QR, statistics, members, attention items, and CSV.\n2) My Khatms lets you edit title, welcome, visibility, allowed platforms, reminder tone, deadline, and safe goal increases. Goal decreases and Quran restructuring stay locked to protect history.\n3) Text, photo, video, or voice broadcasts are sent after content approval and can target by khatm, province, and gender.\n4) A paid khatm can be cancelled with an internal refund only before the first member joins.\n\nMember data is private to that khatm's creator and authorized admins.",
    },
    "help.button.join": {"fa": "👋 شروع و عضویت", "ar": "👋 البدء والانضمام", "en": "👋 Start and Join"},
    "help.button.portion": {"fa": "📖 سهم و انجام", "ar": "📖 الحصة والإنجاز", "en": "📖 Portions and Completion"},
    "help.button.create": {"fa": "➕ ساخت ختم", "ar": "➕ إنشاء ختمة", "en": "➕ Create a Khatm"},
    "help.button.wallet": {"fa": "💳 کیف پول", "ar": "💳 المحفظة", "en": "💳 Wallet"},
    "help.button.settings": {"fa": "⚙️ تنظیمات", "ar": "⚙️ الإعدادات", "en": "⚙️ Settings"},
    "help.button.manage": {"fa": "🧭 مدیریت ختم", "ar": "🧭 إدارة الختمة", "en": "🧭 Manage Khatm"},
    "help.button.balance": {"fa": "💰 دیدن موجودی و شارژ", "ar": "💰 الرصيد والشحن", "en": "💰 Balance and Top Up"},
    "help.button.invoices": {"fa": "🧾 فاکتورها و رسیدهای من", "ar": "🧾 فواتيري وإيصالاتي", "en": "🧾 My Invoices and Receipts"},
    "help.button.back": {"fa": "🔙 برگشت به موضوعات راهنما", "ar": "🔙 العودة إلى مواضيع الدليل", "en": "🔙 Back to Guide Topics"},
    "help.button.open_settings": {"fa": "⚙️ بازکردن تنظیمات", "ar": "⚙️ فتح الإعدادات", "en": "⚙️ Open Settings"},
    "help.button.edit_profile": {"fa": "✏️ ویرایش مشخصات", "ar": "✏️ تعديل الملف", "en": "✏️ Edit Profile"},
    "help.button.change_phone": {"fa": "📱 تغییر شماره", "ar": "📱 تغيير الرقم", "en": "📱 Change Phone"},
    "help.button.link_account": {"fa": "🔗 اتصال حساب قبلی", "ar": "🔗 ربط حساب سابق", "en": "🔗 Link Previous Account"},
    "help.button.start_create": {"fa": "➕ شروع ساخت ختم", "ar": "➕ بدء إنشاء ختمة", "en": "➕ Start Creating"},
    "help.button.request_type": {"fa": "📝 درخواست نوع ختم جدید", "ar": "📝 طلب نوع ختمة جديد", "en": "📝 Request a New Khatm Type"},
    "help.button.my_khatms": {"fa": "🕋 دیدن ختم‌های من", "ar": "🕋 عرض ختماتي", "en": "🕋 View My Khatms"},
    "help.button.creator_panel": {"fa": "📊 بازکردن پنل سازنده", "ar": "📊 فتح لوحة المنشئ", "en": "📊 Open Creator Panel"},
    "help.button.admin_panel": {"fa": "🛠 بازکردن پنل ادمین", "ar": "🛠 فتح لوحة الإدارة", "en": "🛠 Open Admin Panel"},

    # --- create_khatm.py wizard (2026-09-20) ---
    "create_khatm.intro_continue": {"fa": "➡️ ادامه", "ar": "➡️ متابعة", "en": "➡️ Continue"},
    "create_khatm.ask_template": {
        "fa": "چه نوع ختمی می‌خواید بسازید؟", "ar": "ما نوع الختمة التي تريد إنشاءها؟",
        "en": "What kind of khatm do you want to create?",
    },
    "create_khatm.category_prompt.SALAWAT": {
        "fa": "کدام نوع صلوات را می‌خواهید؟", "ar": "أي نوع من الصلوات تريد؟", "en": "Which type of Salawat do you want?",
    },
    "create_khatm.category_prompt.DUA": {
        "fa": "کدام دعا یا زیارت را می‌خواهید؟", "ar": "أي دعاء أو زيارة تريد؟", "en": "Which dua or ziyarat do you want?",
    },
    "create_khatm.category_prompt.LAAN": {
        "fa": "کدام لعن را می‌خواهید؟", "ar": "أي لعن تريد؟", "en": "Which la'an do you want?",
    },
    "create_khatm.category_empty": {
        "fa": "هنوز گزینه‌ای در این بخش فعال نشده است. مدیریت باید ابتدا زیرمجموعه‌های این بخش را اضافه کند.",
        "ar": "لم يتم تفعيل أي خيار في هذا القسم بعد. يجب على الإدارة إضافة خيارات هذا القسم أولاً.",
        "en": "No option has been activated in this section yet. An admin must add items here first.",
    },
    "create_khatm.custom_request_dua_only": {
        "fa": "درخواست آزاد فقط در بخش دعا و زیارت است.",
        "ar": "الطلب الحر متاح فقط في قسم الدعاء والزيارة.",
        "en": "A custom request is only available in the Dua/Ziyarat section.",
    },
    "create_khatm.ask_custom_dua_title": {
        "fa": "اسم دعا یا زیارتی که می‌خواید رو بنویسید؛ درخواستتون برای ادمین ارسال می‌شه و بعد از اضافه شدن به لیست، می‌تونید دوباره از همین‌جا ختمش رو بسازید.",
        "ar": "اكتب اسم الدعاء أو الزيارة الذي تريده؛ سيُرسل طلبك إلى الإدارة، وبعد إضافته للقائمة يمكنك إنشاء ختمة له من هنا.",
        "en": "Type the name of the dua or ziyarat you want; your request is sent to an admin, and once added to the list you can create a khatm for it from here.",
    },
    "create_khatm.custom_dua_title_required": {
        "fa": "لطفاً اسم دعا یا زیارت رو بنویسید.", "ar": "يرجى كتابة اسم الدعاء أو الزيارة.",
        "en": "Please enter the name of the dua or ziyarat.",
    },
    "create_khatm.custom_dua_title_too_long": {
        "fa": "این اسم خیلی بلنده؛ یک اسم کوتاه‌تر بفرستید.", "ar": "هذا الاسم طويل جداً؛ أرسل اسماً أقصر.",
        "en": "That name is too long; please send a shorter one.",
    },
    "create_khatm.custom_dua_submitted": {
        "fa": "درخواست «{title}» برای مدیریت ارسال شد ✅\nبعد از بررسی، به لیست دعاها اضافه می‌شه.",
        "ar": "أُرسل طلب «{title}» إلى الإدارة ✅\nبعد المراجعة سيُضاف إلى قائمة الأدعية.",
        "en": "Your request for “{title}” was sent to an admin ✅\nOnce reviewed, it will be added to the dua list.",
    },
    "create_khatm.category_gone": {
        "fa": "این گزینه دیگر در دسترس نیست.", "ar": "هذا الخيار لم يعد متاحاً.", "en": "This option is no longer available.",
    },
    "create_khatm.mode_explanation.quran": {
        "fa": (
            "🔒 <b>تعهدی:</b> صفحاتی که تعیین می‌کنید، سر ساعت انتخابی خودِ مخاطب برایش ارسال می‌شود "
            "تا به یک روتین روزانه برایش تبدیل شود. اعضا تا مهلت روزانه فرصت دارند بخوانند؛ اگر نخوانند، "
            "ختم منتظرشان می‌ماند و پیشرفت کل جمع کند می‌شود.\n\n"
            "🌿 <b>آزاد:</b> ارسال منظم ساعتی ندارد؛ مخاطبان هر زمان که دوست داشتند وارد بات می‌شوند، "
            "سهم می‌گیرند، پس از قرائت تأیید می‌کنند و ختم این‌گونه با مشارکت جمع جلو می‌رود."
        ),
        "ar": (
            "🔒 <b>ملتزمة:</b> يحصل كل عضو على جزء محدد من القرآن ويلتزم بقراءته "
            "قبل الموعد اليومي. إذا فاته يوم، تنتظره الختمة ويتباطأ التقدم الكلي — "
            "فهذا الالتزام يؤثر فعلاً على الختمة كلها.\n\n"
            "🌿 <b>مفتوحة:</b> لا يوجد نصيب محدد لأحد؛ كل شخص يقرأ ويسجل أي عدد "
            "من الصفحات وفي أي وقت يريد."
        ),
        "en": (
            "🔒 <b>Commitment:</b> each member gets a specific Quran portion and "
            "pledges to read it by the daily deadline. If they miss a day, the khatm "
            "waits on them and everyone's progress slows down — this commitment really "
            "does affect the whole khatm.\n\n"
            "🌿 <b>Open:</b> nobody has a fixed portion; everyone reads and logs "
            "as many pages as they want, whenever they want."
        ),
    },
    "create_khatm.mode_explanation.salawat": {
        "fa": (
            "🔒 <b>تعهدی:</b> تعداد صلواتی که تعیین می‌کنید، سر ساعت انتخابی مخاطب برایش ارسال می‌شود "
            "تا به یک روتین روزانه تبدیل شود و متعهد می‌شود آن را بخواند تا ختم کامل شود.\n\n"
            "🌿 <b>آزاد:</b> ارسال منظم ساعتی ندارد؛ هرکس هر زمان وارد بات شد، هر تعداد صلوات که خواست "
            "می‌فرستد و ثبت می‌کند تا هدف کل ختم کامل شود."
        ),
        "ar": (
            "🔒 <b>ملتزمة:</b> يلتزم كل عضو بإرسال عدد محدد من الصلوات (تحدده أنت، "
            "مثلاً ۱۰۰) حتى النهاية.\n\n"
            "🌿 <b>مفتوحة:</b> لا يوجد التزام؛ كل شخص يرسل ويسجل أي عدد يريده حتى "
            "يكتمل هدف الختمة."
        ),
        "en": (
            "🔒 <b>Commitment:</b> each member pledges to send a fixed number of "
            "Salawat (you set it, e.g. 100) by the end.\n\n"
            "🌿 <b>Open:</b> there's no pledge; everyone sends and logs as much as "
            "they want until the khatm's total goal is reached."
        ),
    },
    "create_khatm.mode_explanation.dua": {
        "fa": (
            "🔒 <b>تعهدی:</b> سهم مشخص‌شده از دعا سر ساعت انتخابی مخاطب ارسال می‌شود تا به یک روتین معنوی روزانه "
            "تبدیل شود و متعهد به قرائت آن است تا ختم معطل نماند.\n\n"
            "🌿 <b>آزاد:</b> ارسال منظم ساعتی ندارد؛ هرکس هر زمان مایل بود وارد بات می‌شود و هرچقدر خواست "
            "می‌خواند و ثبت می‌کند."
        ),
        "ar": (
            "🔒 <b>ملتزمة:</b> يلتزم كل عضو بقراءة عدد محدد (تحدده أنت) من هذا "
            "الدعاء أو الزيارة.\n\n"
            "🌿 <b>مفتوحة:</b> لا يوجد التزام؛ كل شخص يقرأ ويسجل أي عدد يريده حتى "
            "يكتمل هدف الختمة."
        ),
        "en": (
            "🔒 <b>Commitment:</b> each member pledges to recite a fixed number "
            "(you set it) of this dua or ziyarat.\n\n"
            "🌿 <b>Open:</b> there's no pledge; everyone reads and logs as much as "
            "they want until the khatm's total goal is reached."
        ),
    },
    "create_khatm.mode_explanation.laan": {
        "fa": (
            "🔒 <b>تعهدی:</b> تعداد مشخص از ذکر سر ساعت انتخابی مخاطب ارسال می‌شود تا به یک روتین منظم تبدیل شود "
            "و متعهد به قرائت آن در مهلت روزانه است.\n\n"
            "🌿 <b>آزاد:</b> ارسال منظم ساعتی ندارد؛ هرکس هر زمان خواست وارد بات می‌شود و هرچقدر خواست "
            "می‌خواند و ثبت می‌کند."
        ),
        "ar": (
            "🔒 <b>ملتزمة:</b> يلتزم كل عضو بقول عدد محدد (تحدده أنت) من هذا "
            "اللعن.\n\n"
            "🌿 <b>مفتوحة:</b> لا يوجد التزام؛ كل شخص يقول ويسجل أي عدد يريده حتى "
            "يكتمل هدف الختمة."
        ),
        "en": (
            "🔒 <b>Commitment:</b> each member pledges to recite a fixed number "
            "(you set it) of this la'an.\n\n"
            "🌿 <b>Open:</b> there's no pledge; everyone recites and logs as much "
            "as they want until the khatm's total goal is reached."
        ),
    },
    "create_khatm.ask_mode": {
        "fa": "این ختم تعهدی باشه یا آزاد؟\n\n{explanation}",
        "ar": "هل تكون هذه الختمة ملتزمة أم مفتوحة؟\n\n{explanation}",
        "en": "Should this khatm be commitment-based or open?\n\n{explanation}",
    },
    "create_khatm.default_title.quran": {
        "fa": "ختم قرآن", "ar": "ختمة القرآن", "en": "Quran khatm",
    },
    "create_khatm.default_title.salawat": {
        "fa": "ختم صلوات", "ar": "ختمة الصلوات", "en": "Salawat khatm",
    },
    "create_khatm.default_title.category": {
        "fa": "ختم {name}", "ar": "ختمة {name}", "en": "{name} khatm",
    },
    "create_khatm.fixed_niyyat": {
        "fa": "به نیت ظهور امام زمان عجل الله تعالی فرجه الشریف",
        "ar": "بنية ظهور الإمام المهدي عجل الله فرجه",
        "en": "For the reappearance of Imam Mahdi, may Allah hasten his reappearance",
    },
    "create_khatm.niyyat_proxy_suffix": {
        "fa": " — به نیابت از {name}",
        "ar": " — نيابةً عن {name}",
        "en": " — on behalf of {name}",
    },
    "create_khatm.ask_niyyat": {
        "fa": "همهٔ ختم‌ها به نیت ظهور امام زمان عجل الله تعالی فرجه الشریف هستند.\n\n"
              "اگر می‌خواهید این ختم را به نیابت از شخصی و برای حاجتی هم ثبت کنید، بنویسید (اختیاری). مثلاً:\n"
              "• به نیابت از پدرم مرحوم حاج حسین…\n"
              "• به نیابت از برادرم، برای شفای ایشان…\n\n"
              "یا اگر نمی‌خواهید، دکمهٔ رد کردن را بزنید.",
        "ar": "كل الختمات بنية ظهور الإمام المهدي عجل الله تعالى فرجه الشريف.\n\n"
              "إن أردت تسجيلها بنيّة أو نيابة خاصة أيضاً، فاكتبها (اختياري). مثلاً:\n"
              "• نيابةً عن والدي المرحوم الحاج حسين…\n"
              "• بنيّة شفاء أخي…\n\n"
              "وإن لم ترغب، اضغط زر التخطي.",
        "en": "Every khatm is for the reappearance of Imam Mahdi, may Allah hasten his reappearance.\n\n"
              "If you'd also like to register a specific dedication or intention, type it (optional). For example:\n"
              "• On behalf of my late father, Haj Hossein…\n"
              "• For the healing of my brother…\n\n"
              "Or tap skip if you'd rather not.",
    },
    # Owner request (2026-09-21): the welcome-message prompt should suggest
    # an example matching the actual khatm content (Quran/Salawat/Dua/La'an),
    # not a one-size-fits-all example — still fully optional/skippable.
    "create_khatm.welcome_intro": {
        "fa": "یک پیام خوش‌آمد بنویسید که هر عضو جدید همون لحظهٔ عضویت ببینه.",
        "ar": "اكتب رسالة ترحيب يراها كل عضو جديد لحظة انضمامه.",
        "en": "Write a welcome message every new member sees the moment they join.",
    },
    "create_khatm.ask_creator_contact": {
        "fa": "برای اینکه اگر مخاطبان ختم شما مشکلی داشتند بتوانند با شما ارتباط بگیرند، آیدی تلگرام یا بله‌تون رو بفرستید (اگه آیدی ندارید، شماره‌تون). این راه ارتباطی در پیام خوش‌آمد قرار می‌گیره. (این مرحله لازمه)",
        "ar": "كي يتمكن الأعضاء من التواصل معك، أرسل معرّفك في تلگرام أو بله (أو رقمك إن لم يكن لديك معرّف). سيظهر في رسالة الترحيب. (هذه الخطوة إلزامية)",
        "en": "So members can reach you, send your Telegram or Bale ID (or your phone if you have no ID). It'll appear in the welcome message. (This step is required)",
    },
    "create_khatm.creator_contact_required": {
        "fa": "این مرحله لازمه 🙏 لطفاً یه آیدی (تلگرام/بله) یا شمارهٔ تماس بفرستید تا اعضا بتونن باهاتون ارتباط بگیرن.",
        "ar": "هذه الخطوة إلزامية 🙏 أرسل معرّفاً (تلگرام/بله) أو رقم هاتف ليتمكن الأعضاء من التواصل معك.",
        "en": "This step is required 🙏 Please send an ID (Telegram/Bale) or a phone number so members can contact you.",
    },
    "create_khatm.contact.use_username": {
        "fa": "همین راه ارتباطی خودم: {username}",
        "ar": "استخدم وسيلة التواصل الخاصة بي: {username}",
        "en": "Use my contact: {username}",
    },
    "create_khatm.welcome_contact_line": {
        "fa": "📬 برای ارتباط با سازندهٔ ختم: {contact}",
        "ar": "📬 للتواصل مع منظّم الختمة: {contact}",
        "en": "📬 To reach the Khatm organizer: {contact}",
    },
    # ---- R11/N2 (owner 2026-09-28): member-side commitment mode -------------
    "commit.explain": {
        "fa": "این ختم تعهدی است 🌱 دو راه برای شرکت داری:\n\n• <b>تعهد منظم</b>: سر ساعتی که انتخاب می‌کنی (هر روز/هفته/ماه) برات یادآوری می‌شه.\n• <b>تعهد تعدادی</b>: یک تعداد مشخص می‌کنی و خودت می‌خونی و ثبت می‌کنی (در این مدل برای شما یادآوری ارسال نمی‌شود).\n\nروشی را انتخاب کن که انجام‌دادنش برایت راحت‌تر و مطمئن‌تر است.",
        "ar": "هذه ختمة ملتزمة 🌱 لديك طريقتان للمشاركة:\n\n• <b>التزام منتظم</b>: يصلك تذكير في الوقت الذي تختاره (يوميًا/أسبوعيًا/شهريًا).\n• <b>التزام بعدد</b>: تحدد عددًا معينًا وتقرأه بنفسك وتسجّله (في هذا الخيار لا يتم إرسال تذكير).\n\nفي كلتا الحالتين عليك القراءة — يختلف أسلوب التذكير فقط.",
        "en": "This is a commitment Khatm 🌱 Two ways to take part:\n\n• <b>Regular</b>: you get a reminder at a time you pick (daily/weekly/monthly).\n• <b>By count</b>: you pledge a number, read it yourself, and log it.\n\nEither way you read — only the reminder style differs.",
    },
    "commit.ask_mode": {
        "fa": "چطور می‌خوای بخونی؟",
        "ar": "كيف تريد أن تقرأ؟",
        "en": "How would you like to read?",
    },
    "commit.mode.regular": {"fa": "🔁 تعهد منظم", "ar": "🔁 التزام منتظم", "en": "🔁 Regular schedule"},
    "commit.mode.count": {"fa": "🔢 تعهد تعدادی", "ar": "🔢 التزام بعدد", "en": "🔢 By count"},
    "commit.ask_count": {
        "fa": "چند بار می‌خوای بخونی؟ عدد رو بنویس (مثلاً 100).",
        "ar": "كم مرة تريد أن تقرأ؟ اكتب العدد (مثلاً 100).",
        "en": "How many times will you read? Type a number (e.g. 100).",
    },
    "commit.ask_count.salawat": {
        "fa": "چه تعداد صلوات می‌فرستید؟ عدد رو بنویسید (مثلاً 100).",
        "ar": "كم صلاة سترسل؟ اكتب العدد (مثلاً 100).",
        "en": "How many Salawat will you send? Type a number (e.g. 100).",
    },
    "commit.ask_count.dua": {
        "fa": "چند بار می‌خواهید این دعا یا زیارت را بخوانید؟ عدد را بنویسید.",
        "ar": "كم مرة تريد قراءة هذا الدعاء أو الزيارة؟ اكتب العدد.",
        "en": "How many times will you read this dua or ziyarat? Type a number.",
    },
    "commit.ask_count.laan": {
        "fa": "چه تعداد لعن می‌فرستید؟ عدد را بنویسید.",
        "ar": "كم مرة ستقرأ اللعن؟ اكتب العدد.",
        "en": "How many la'an recitations will you make? Type a number.",
    },
    "commit.ask_count_invalid": {
        "fa": "یک عدد درست بنویس (مثلاً 100).",
        "ar": "اكتب عددًا صحيحًا (مثلاً 100).",
        "en": "Please type a valid number (e.g. 100).",
    },
    "commit.ask_freq": {
        "fa": "هر چند وقت یک‌بار؟",
        "ar": "كم مرة؟",
        "en": "How often?",
    },
    "commit.period.day": {"fa": "روز", "ar": "يوم", "en": "day"},
    "commit.period.week": {"fa": "هفته", "ar": "أسبوع", "en": "week"},
    "commit.period.month": {"fa": "ماه", "ar": "شهر", "en": "month"},
    "commit.period.these_days": {"fa": "روز انتخاب‌شده", "ar": "يوم محدد", "en": "selected day"},
    "commit.ask_weekdays": {
        "fa": "کدام روزهای هفته؟ روزهای موردنظر را بزنید (می‌توانید چند روز انتخاب کنید) و بعد «تأیید روزها» را بزنید.",
        "ar": "أي أيام الأسبوع؟ اختر الأيام (يمكن اختيار عدة أيام) ثم اضغط «تأكيد الأيام».",
        "en": "Which days of the week? Tap the days you want (you can pick several), then tap “Confirm days”.",
    },
    "commit.weekdays_confirm": {"fa": "✅ تأیید روزها", "ar": "✅ تأكيد الأيام", "en": "✅ Confirm days"},
    "commit.weekdays_need_one": {"fa": "حداقل یک روز را انتخاب کنید.", "ar": "اختر يوماً واحداً على الأقل.", "en": "Pick at least one day."},
    "commit.ask_times_per_period": {
        "fa": "چند بار در {period} می‌خوای بخونی؟ عدد رو بنویس (مثلاً 3).",
        "ar": "كم مرة في ال{period} تريد أن تقرأ؟ اكتب العدد (مثلاً 3).",
        "en": "How many times per {period} will you read? Type a number (e.g. 3).",
    },
    "commit.ask_times_per_period.salawat": {
        "fa": "در هر {period} چه تعداد صلوات می‌فرستید؟ عدد را بنویسید.",
        "ar": "كم صلاة سترسل في كل {period}؟ اكتب العدد.",
        "en": "How many Salawat will you send per {period}? Type a number.",
    },
    "commit.ask_times_per_period.dua": {
        "fa": "در هر {period} چند بار می‌خواهید این دعا یا زیارت را بخوانید؟ عدد را بنویسید (مثلاً ۲). اگر چند روز انتخاب کرده‌اید، این عدد برای تک‌تک آن روزهاست.",
        "ar": "كم مرة ستقرأ هذا الدعاء أو الزيارة في كل {period}؟",
        "en": "How many times per {period} will you read this dua or ziyarat?",
    },
    "commit.ask_times_per_period.laan": {
        "fa": "در هر {period} چه تعداد لعن می‌فرستید؟ عدد را بنویسید.",
        "ar": "كم مرة ستقرأ اللعن في كل {period}؟ اكتب العدد.",
        "en": "How many la'an recitations per {period}? Type a number.",
    },
    "commit.hour.custom": {
        "fa": "🕒 ساعت دلخواه (مثلاً 13:25)",
        "ar": "🕒 وقت مخصص (مثلاً 13:25)",
        "en": "🕒 Custom time (e.g. 13:25)",
    },
    "commit.ask_custom_time": {
        "fa": "ساعت دقیق یادآوری رو بنویس (مثلاً 13:25):",
        "ar": "اكتب وقت التذكير الدقيق (مثلاً 13:25):",
        "en": "Type the exact reminder time (e.g. 13:25):",
    },
    "commit.ask_custom_time_invalid": {
        "fa": "ساعت رو به شکل درست بنویس، مثلاً 13:25 (بین 00:00 تا 23:59).",
        "ar": "اكتب الوقت بشكل صحيح، مثلاً 13:25 (بين 00:00 و23:59).",
        "en": "Type a valid time like 13:25 (between 00:00 and 23:59).",
    },
    "commit.freq.daily": {"fa": "هر روز", "ar": "كل يوم", "en": "Every day"},
    "commit.freq.weekly": {"fa": "هر هفته", "ar": "كل أسبوع", "en": "Every week"},
    "commit.freq.monthly": {"fa": "هر ماه", "ar": "كل شهر", "en": "Every month"},
    "commit.ask_weekday": {
        "fa": "کدام روز هفته؟",
        "ar": "أي يوم من الأسبوع؟",
        "en": "Which day of the week?",
    },
    "commit.ask_monthday": {
        "fa": "کدام روز ماه؟ عددی بین ۱ تا ۳۱ بنویس.",
        "ar": "أي يوم من الشهر؟ اكتب رقمًا بين 1 و31.",
        "en": "Which day of the month? Type a number from 1 to 31.",
    },
    "commit.ask_monthday_invalid": {
        "fa": "یک عدد بین ۱ تا ۳۱ بنویس.",
        "ar": "اكتب رقمًا بين 1 و31.",
        "en": "Type a number from 1 to 31.",
    },
    "commit.ask_per_occurrence": {
        "fa": "هر بار چند تا می‌خوای بخونی؟ عدد رو بنویس.",
        "ar": "كم تقرأ في كل مرة؟ اكتب العدد.",
        "en": "How many each time? Type a number.",
    },
    "commit.ask_hour": {
        "fa": "چه ساعتی برات یادآوری بشه؟",
        "ar": "في أي ساعة نذكّرك؟",
        "en": "What time should we remind you?",
    },
    "commit.regular_saved": {
        "fa": "✅ تنظیم شد! مجموعاً {times} مرتبه در {period}، ساعت {hour} یادآوری و سهم‌تون خودکار فرستاده می‌شه. 🌱",
        "ar": "✅ تم الضبط! {times} مرة في ال{period}، الساعة {hour} تُرسل لك حصتك تلقائياً. 🌱",
        "en": "✅ Set! {times} time(s) per {period}, at {hour} your share will be sent automatically. 🌱",
    },
    "navigation.back_home": {
        "fa": "🏠 منوی اصلی", "ar": "🏠 القائمة الرئيسية", "en": "🏠 Main menu",
    },
    "commit.regular.done_button": {
        "fa": "✅ قرائت بخش فوق انجام شد", "ar": "✅ أنجزت حصتي", "en": "✅ Mark share done",
    },
    "commit.regular.done_confirmed": {
        "fa": "✅ قرائت شما ({count} مرتبه) در سیستم ثبت شد و شما در ثواب این ختم شریک شدید.\n\nبا تشکر 🌱",
        "ar": "✅ تم تسجيل إنجاز حصتك: {count} مرة. تقبل الله 🌱",
        "en": "✅ Your share was recorded: {count} time(s).",
    },
    "commit.regular.already_done": {
        "fa": "این سهم قبلاً انجام شده و ثبت شده است.",
        "ar": "تم إنجاز هذه الحصة وتسجيلها مسبقًا.",
        "en": "This share has already been completed and recorded.",
    },
    "commit.regular.invalid": {
        "fa": "این سهم برای شما فعال نیست.",
        "ar": "هذه الحصة غير مفعلة لك.",
        "en": "This share is not active for you.",
    },
    "commit.count_saved": {
        "fa": "✅ تعهد شما با موفقیت ثبت شد: {target} مرتبه. پس از انجام، با دکمهٔ زیر ثبت نمایید. 🌱",
        "ar": "✅ تم تسجيل التزامك: {target} مرة. بعد الأداء، سجّله بالزر أدناه. 🌱",
        "en": "✅ Your pledge is set: {target} times. Log it with the button below when completed. 🌱",
    },
    "commit.count_logged": {
        "fa": "ثبت شد 🌱 تا حالا {done} از {target}.",
        "ar": "تم التسجيل 🌱 حتى الآن {done} من {target}.",
        "en": "Logged 🌱 {done} of {target} so far.",
    },
    "commit.count_completed": {
        "fa": "🎉 طاعت و همراهی‌تان قبول حق! تعهد شما کامل شد ({target} مرتبه). در صورت تمایل می‌توانید تعهد جدیدی ثبت نمایید. 🌱",
        "ar": "🎉 تقبّل الله طاعتكم! أكملتم التزامكم ({target} مرة). إن أحببتم، يمكنكم تسجيل التزام جديد. 🌱",
        "en": "🎉 Well done! You completed your pledge ({target} times). Pledge again if you like. 🌱",
    },
    "commit.count.log_one": {"fa": "✅ ۱ سهم انجام شد", "ar": "✅ أنجزت حصة واحدة", "en": "✅ 1 portion done"},
    "commit.count.log_custom": {"fa": "🔢 تعداد دلخواه", "ar": "🔢 عدد مخصص", "en": "🔢 Custom amount"},
    "commit.count.new_pledge": {"fa": "➕ تعهد جدید", "ar": "➕ التزام جديد", "en": "➕ New pledge"},
    "commit.ask_log_amount": {
        "fa": "چه تعداد انجام دادید؟ عدد را بنویسید:",
        "ar": "كم أنجزت؟ اكتب العدد:",
        "en": "How many did you complete? Type a number:",
    },
    "intro.image_caption.QURAN": {
        "fa": (
            "مخاطبان شما وارد بات «ختم قرآن برای صاحب‌الزمان» می‌شوند.\n"
            "همهٔ ختم‌ها به نیت ظهور امام زمان عجل الله تعالی فرجه الشریف برگزار می‌شوند 🌱\n"
            "(البته می‌توانید نیابت خاص هم برای ختم مشخص کنید؛ مثلاً: به نیابت از مرحوم مادرم فلانی به نیت فرج امام زمان عجل الله...)"
        ),
        "ar": "يدخل جمهورك إلى بوت «ختمة القرآن لصاحب الزمان».\nجميع الختمات بنية ظهور الإمام المهدي عجل الله تعالى فرجه الشريف 🌱",
        "en": "Your audience enters the “Quran Khatm for Sahib al-Zaman” bot.\nEvery khatm is dedicated to the reappearance of Imam Mahdi (AJ) 🌱",
    },
    "intro.image_caption.SALAWAT": {
        "fa": (
            "مخاطبان شما وارد بات «ختم صلوات برای صاحب‌الزمان» می‌شوند.\n"
            "همهٔ ختم‌ها به نیت ظهور امام زمان عجل الله تعالی فرجه الشریف برگزار می‌شوند 🌱\n"
            "(البته می‌توانید نیابت خاص هم برای ختم مشخص کنید؛ مثلاً: به نیابت از مرحوم مادرم فلانی به نیت فرج امام زمان عجل الله...)"
        ),
        "ar": "يدخل جمهورك إلى بوت «ختمة الصلوات لصاحب الزمان».\nجميع الختمات بنية ظهور الإمام المهدي عجل الله تعالى فرجه الشريف 🌱",
        "en": "Your audience enters the “Salawat Khatm for Sahib al-Zaman” bot.\nEvery khatm is dedicated to the reappearance of Imam Mahdi (AJ) 🌱",
    },
    "intro.image_caption.DUA_ZIYARAT": {
        "fa": (
            "مخاطبان شما وارد بات «ختم دعا و زیارت برای صاحب‌الزمان» می‌شوند.\n"
            "همهٔ ختم‌ها به نیت ظهور امام زمان عجل الله تعالی فرجه الشریف برگزار می‌شوند 🌱\n"
            "(البته می‌توانید نیابت خاص هم برای ختم مشخص کنید؛ مثلاً: به نیابت از مرحوم مادرم فلانی به نیت فرج امام زمان عجل الله...)"
        ),
        "ar": "يدخل جمهورك إلى بوت «ختمة الدعاء والزيارة لصاحب الزمان».\nجميع الختمات بنية ظهور الإمام المهدي عجل الله تعالى فرجه الشريف 🌱",
        "en": "Your audience enters the “Dua and Ziyarat Khatm for Sahib al-Zaman” bot.\nEvery khatm is dedicated to the reappearance of Imam Mahdi (AJ) 🌱",
    },
    "intro.image_caption.LAAN": {
        "fa": (
            "مخاطبان شما وارد بات «ختم لعن برای صاحب‌الزمان» می‌شوند.\n"
            "همهٔ ختم‌ها به نیت ظهور امام زمان عجل الله تعالی فرجه الشریف برگزار می‌شوند 🌱\n"
            "(البته می‌توانید نیابت خاص هم برای ختم مشخص کنید؛ مثلاً: به نیابت از مرحوم مادرم فلانی به نیت فرج امام زمان عجل الله...)"
        ),
        "ar": "يدخل جمهورك إلى بوت «ختمة اللعن لصاحب الزمان».\nجميع الختمات بنية ظهور الإمام المهدي عجل الله تعالى فرجه الشريف 🌱",
        "en": "Your audience enters the “La'an Khatm for Sahib al-Zaman” bot.\nEvery khatm is dedicated to the reappearance of Imam Mahdi (AJ) 🌱",
    },
    "reminder.regular_commitment": {
        "fa": "🌱 وقت خواندن سهم شما از «{title}» است: {count} مرتبه.",
        "ar": "🌱 حان وقت قراءة نصيبك من «{title}»: {count} مرة.",
        "en": "🌱 Time to read your share of “{title}”: {count} time(s).",
    },
    "weekday.sat": {"fa": "شنبه", "ar": "السبت", "en": "Sat"},
    "weekday.sun": {"fa": "یکشنبه", "ar": "الأحد", "en": "Sun"},
    "weekday.mon": {"fa": "دوشنبه", "ar": "الاثنين", "en": "Mon"},
    "weekday.tue": {"fa": "سه‌شنبه", "ar": "الثلاثاء", "en": "Tue"},
    "weekday.wed": {"fa": "چهارشنبه", "ar": "الأربعاء", "en": "Wed"},
    "weekday.thu": {"fa": "پنجشنبه", "ar": "الخميس", "en": "Thu"},
    "weekday.fri": {"fa": "جمعه", "ar": "الجمعة", "en": "Fri"},
    "create_khatm.welcome_example.quran": {
        "fa": "\n\nمثلاً: «صفحه‌های امروزتون رو با یاد صلوات بر محمد و آل محمد بخونید» یا یک آیهٔ کوتاه.",
        "ar": "\n\nمثلاً: «اقرأ صفحاتك اليوم مع الصلاة على محمد وآل محمد» أو آية قصيرة.",
        "en": "\n\nExample: “Read today's pages while sending blessings on Muhammad and his family” or a short verse.",
    },
    "create_khatm.welcome_example.salawat": {
        "fa": "\n\nمثلاً: «این صلوات‌ها هدیه به روح پدر مرحومم باشه» یا یک حدیث کوتاه دربارهٔ فضیلت صلوات.",
        "ar": "\n\nمثلاً: «هذه الصلوات هدية لروح والدي المرحوم» أو حديث قصير عن فضل الصلاة.",
        "en": "\n\nExample: “These Salawat are a gift to my late father's soul” or a short hadith on the virtue of Salawat.",
    },
    "create_khatm.welcome_example.dua": {
        "fa": "\n\nمثلاً: «این دعا رو با نیت سلامتی خانواده‌مون می‌خونیم».",
        "ar": "\n\nمثلاً: «نقرأ هذا الدعاء بنية سلامة عائلتنا».",
        "en": "\n\nExample: “We're reciting this dua for our family's well-being.”",
    },
    "create_khatm.welcome_example.laan": {
        "fa": "\n\nمثلاً: «این لعن را به نیت ظهور امام زمان علیه‌السلام می‌خوانیم».",
        "ar": "\n\nمثلاً: «نقول هذا اللعن بنية الفرج».",
        "en": "\n\nExample: “We're reciting this la'an with the intention of a swift relief.”",
    },
    "create_khatm.welcome_suffix": {
        "fa": "\n\n(اختیاری، حداکثر ۵۰۰ کاراکتر؛ اگه نمی‌خواید چیزی بنویسید، دکمهٔ رد کردن رو بزنید):",
        "ar": "\n\n(اختياري، حتى ۵۰۰ حرف؛ إذا لا تريد كتابة شيء اضغط زر التخطي):",
        "en": "\n\n(optional, up to 500 characters; tap Skip if you don't want to write one):",
    },
    "create_khatm.welcome_too_long": {
        "fa": "پیام خوش‌آمد نباید بیشتر از ۵۰۰ کاراکتر باشد.",
        "ar": "لا يجوز أن تتجاوز رسالة الترحيب ۵۰۰ حرف.",
        "en": "The welcome message cannot exceed 500 characters.",
    },
    "create_khatm.ask_creator_display": {
        "fa": "اسم شما به‌عنوان سازندهٔ این ختم، جلوی چشم اعضا چطور نشون داده بشه؟ (این فقط روی نمایش تأثیر داره، هویت واقعی شما همیشه پیش خود بات محفوظه)",
        "ar": "كيف يظهر اسمك كمنشئ لهذه الختمة أمام الأعضاء؟ (يؤثر فقط على العرض؛ هويتك الحقيقية محفوظة دائماً لدى البوت)",
        "en": "How should your name as the creator appear to members? (This only affects display — your real identity always stays with the bot)",
    },
    "create_khatm.ask_pseudonym": {
        "fa": "نام مؤسسه یا سازمانتان را بنویسید (حداکثر ۶۴ کاراکتر):", "ar": "اكتب اسم مؤسستك أو منظمتك (حتى ۶۴ حرفاً):",
        "en": "Enter your institution or organization name (up to 64 characters):",
    },
    "create_khatm.pseudonym_invalid": {
        "fa": "نام مؤسسه باید بین ۱ تا ۶۴ کاراکتر باشد.", "ar": "يجب أن يكون اسم المؤسسة بين ۱ و۶۴ حرفاً.",
        "en": "The institution name must be between 1 and 64 characters.",
    },
    "create_khatm.ask_start_schedule": {
        "fa": "این ختم همین الان شروع بشه، یا یک تاریخ خاص تو آینده؟\n(اگه تاریخ آینده رو انتخاب کنید، لینک دعوت همین حالا کار می‌کنه و اعضا می‌تونن عضو بشن، ولی سهم‌ها و یادآوری‌ها فقط از همون تاریخ شروع می‌شن)",
        "ar": "هل تبدأ هذه الختمة الآن أم في تاريخ محدد لاحقاً؟\n(إذا اخترت تاريخاً لاحقاً، يعمل رابط الدعوة فوراً ويمكن للأعضاء الانضمام، لكن الحصص والتذكيرات تبدأ فقط من ذلك التاريخ)",
        "en": "Should this khatm start right now, or on a specific future date?\n(If you pick a future date, the invite link works immediately and members can join, but portions and reminders only start on that date)",
    },
    "create_khatm.ask_open_target": {
        "fa": "هدف کل «{title}» چند {unit} باشه؟ فقط عدد بفرستید (مثلاً 1000).\n\nبا تمام‌شدن ختم، مخاطبان نمی‌توانند ادامه دهند؛ اما در آینده امکان افزایش تعداد هست:",
        "ar": "كم يكون الهدف الكلي لـ«{title}» ({unit})؟ أرسل رقماً فقط (مثلاً 1000):",
        "en": "What should the total goal for “{title}” be, in {unit}? Send a number only (e.g. 1000):",
    },
    "create_khatm.ask_commitment_total": {
        "fa": "هدف کل این ختم چند {unit} باشه؟ یکی از دکمه‌ها را بزنید (سهم هر نفر را خودِ شرکت‌کننده تعیین می‌کند).\n\nبا تمام‌شدن ختم، مخاطبان نمی‌توانند ادامه دهند؛ اما در آینده امکان افزایش تعداد هست:",
        "ar": "كم يكون الهدف الكلي لهذه الختمة ({unit})؟ اختر أحد الأزرار (كل مشارك يحدّد حصته بنفسه):",
        "en": "What's the total goal for this khatm, in {unit}? Tap a button (each participant sets their own share):",
    },
    "create_khatm.ask_commitment_total.salawat": {
        "fa": "هدف کل این ختم چه تعداد صلوات باشد؟ سهم روزانه/هفتگی/ماهانه را هر مخاطب برای خودش انتخاب می‌کند.\n\nبا تمام‌شدن ختم، مخاطبان نمی‌توانند ادامه دهند؛ اما در آینده امکان افزایش تعداد هست:",
        "ar": "كم يكون مجموع الصلوات في هذه الختمة؟ يختار كل مشارك حصته بنفسه.",
        "en": "What should the total Salawat goal be? Each member chooses their own schedule.",
    },
    "create_khatm.ask_commitment_total.dua": {
        "fa": "این دعا یا زیارت در مجموع چند بار خوانده شود؟\n\nبا تمام‌شدن ختم، مخاطبان نمی‌توانند ادامه دهند؛ اما در آینده امکان افزایش تعداد هست:",
        "ar": "كم مرة يُقرأ هذا الدعاء أو الزيارة إجمالاً؟",
        "en": "How many times should this dua or ziyarat be read in total?",
    },
    "create_khatm.ask_commitment_total.laan": {
        "fa": "هدف کل این ختم چه تعداد لعن باشد؟ سهم روزانه/هفتگی/ماهانه را هر مخاطب برای خودش انتخاب می‌کند.\n\nبا تمام‌شدن ختم، مخاطبان نمی‌توانند ادامه دهند؛ اما در آینده امکان افزایش تعداد هست:",
        "ar": "كم يكون مجموع اللعن في هذه الختمة؟",
        "en": "What should the total la'an goal be?",
    },
    "create_khatm.commitment_total.custom": {
        "fa": "🔢 عدد دلخواه", "ar": "🔢 رقم مخصص", "en": "🔢 Custom number",
    },
    "create_khatm.commitment_total.unlimited": {
        "fa": "♾ نامحدود", "ar": "♾ غير محدود", "en": "♾ Unlimited",
    },
    "create_khatm.ask_commitment_total_custom": {
        "fa": "عدد هدف کل را بنویسید (مثلاً 5000).\n\nبا تمام‌شدن ختم، مخاطبان نمی‌توانند ادامه دهند؛ اما در آینده امکان افزایش تعداد هست:",
        "ar": "اكتب رقم الهدف الكلي (مثلاً 5000):",
        "en": "Type the total goal number (e.g. 5000):",
    },
    "create_khatm.unit.salawat": {"fa": "صلوات", "ar": "صلاة", "en": "Salawat"},
    "create_khatm.unit.time": {"fa": "مرتبه", "ar": "مرة", "en": "time(s)"},
    "create_khatm.ask_edition": {
        "fa": "کدوم نسخه قرآن رو می‌خواید؟", "ar": "أي نسخة من القرآن تريد؟", "en": "Which Quran edition do you want?",
    },
    "create_khatm.ask_start_at": {
        "fa": "تاریخ و ساعت شروع را به وقت تهران و با قالب YYYY-MM-DD HH:MM بفرستید.",
        "ar": "أرسل تاريخ ووقت البدء بتوقيت طهران بالصيغة YYYY-MM-DD HH:MM.",
        "en": "Send the start date and time in Tehran time, in the format YYYY-MM-DD HH:MM.",
    },
    "create_khatm.start_at_format_invalid": {
        "fa": "قالب تاریخ درست نیست. نمونه: 2026-10-01 09:30", "ar": "صيغة التاريخ غير صحيحة. مثال: 2026-10-01 09:30",
        "en": "Invalid date format. Example: 2026-10-01 09:30",
    },
    "create_khatm.start_at_must_be_future": {
        "fa": "زمان شروع باید در آینده باشد.", "ar": "يجب أن يكون وقت البدء في المستقبل.",
        "en": "The start time must be in the future.",
    },
    "create_khatm.positive_number_required": {
        "fa": "لطفاً فقط یک عدد بزرگ‌تر از صفر بفرستید.", "ar": "يرجى إرسال رقم أكبر من صفر فقط.",
        "en": "Please send only a number greater than zero.",
    },
    "create_khatm.ask_deadline_hour": {
        "fa": "⏰ ساعت پایان روزانهٔ ختم چه ساعتی باشد؟ تا این ساعت فرصت دارند سهم همان روز را بخوانند. یک عدد بین ۰ تا ۲۳ بفرستید (مثلاً برای ۱۱ شب بنویسید 23):",
        "ar": "حتى أي ساعة يومياً مهلة قراءة حصة اليوم؟ أرسل رقماً بين ۰ و۲۳ (مثلاً للساعة ۱۱ مساءً اكتب 23):",
        "en": "Every day, until what hour is today's portion due? Send a number between 0 and 23 (e.g. for 11pm send 23):",
    },
    "create_khatm.hour_required": {
        "fa": "لطفاً فقط یک عدد بین ۰ تا ۲۳ بفرستید.", "ar": "يرجى إرسال رقم بين ۰ و۲۳ فقط.",
        "en": "Please send only a number between 0 and 23.",
    },
    "create_khatm.ask_capacity_number": {
        "fa": "حداکثر چند نفر تعهدی؟ فقط عدد بفرستید (مثلاً 301):",
        "ar": "ما الحد الأقصى لعدد الملتزمين؟ أرسل رقماً فقط (مثلاً 301):",
        "en": "What's the maximum number of committed members? Send a number only (e.g. 301):",
    },
    "create_khatm.ask_reminder_tone": {
        "fa": (
            "پیام‌های یادآوری با چه لحنی فرستاده بشه؟ (فقط حس‌وحال متن، محتوای ختم عوض نمی‌شه)\n\n"
            "🌱 <b>صمیمی</b>: «سلام رفیق! وقت {share} رسیده، بزن بریم 🌿»\n"
            "📜 <b>رسمی</b>: «با سلام، یادآوری می‌شود {share} آمادهٔ انجام است.»\n"
            "🤍 <b>معنوی</b>: «یاد خدا دل را آرام می‌کند؛ {share} منتظر شماست.»\n"
            "⚡ <b>کوتاه</b>: «{share} آماده است.»"
        ),
        "ar": (
            "بأي أسلوب تُرسل رسائل التذكير؟ (يؤثر على الأسلوب فقط، لا يغيّر المحتوى)\n\n"
            "🌱 <b>ودّي</b>: «مرحباً يا صديقي! حان وقت {share} 🌿»\n"
            "📜 <b>رسمي</b>: «تحية طيبة، نذكّرك بأن {share} جاهزة.»\n"
            "🤍 <b>روحاني</b>: «بذكر الله تطمئنّ القلوب؛ {share} بانتظارك.»\n"
            "⚡ <b>مختصر</b>: «{share} جاهزة.»"
        ),
        "en": (
            "In what tone should reminders be sent for {share}? (Only the wording, not the content)\n\n"
            "🌱 <b>Friendly</b>: “Hey friend! Time for today's share, let's go 🌿”\n"
            "📜 <b>Formal</b>: “Greetings. A reminder that your share for today is ready to read.”\n"
            "🤍 <b>Spiritual</b>: “Remembrance of God calms the heart; your share awaits you today.”\n"
            "⚡ <b>Short</b>: “Your share for today is ready.”"
        ),
    },
    "create_khatm.ask_visibility": {
        "fa": "لینک دعوت این ختم چطور کار کنه؟", "ar": "كيف يعمل رابط دعوة هذه الختمة؟",
        "en": "How should this khatm's invite link work?",
    },
    "create_khatm.mode_label.COMMITMENT": {"fa": "تعهدی", "ar": "ملتزمة", "en": "Commitment"},
    "create_khatm.mode_label.OPEN": {"fa": "آزاد", "ar": "مفتوحة", "en": "Open"},
    "create_khatm.visibility_label.PUBLIC": {
        "fa": "لینک عمومی؛ در فهرست ختم‌های عمومی نمایش داده شود", "ar": "رابط عام؛ يظهر في قائمة الختمات العامة", "en": "Public link; show in the public khatm list",
    },
    "create_khatm.visibility_label.UNLISTED": {
        "fa": "با لینک، برای همه باز", "ar": "بالرابط، مفتوحة للجميع", "en": "Link-only, open to anyone",
    },
    "create_khatm.visibility_label.PRIVATE": {
        "fa": "عضویت نیاز به تایید من داره", "ar": "الانضمام يحتاج موافقتي", "en": "Joining needs my approval",
    },
    "create_khatm.display_label.FULL_NAME": {"fa": "نام کامل", "ar": "الاسم الكامل", "en": "Full name"},
    "create_khatm.display_label.FIRST_NAME": {"fa": "نام کوچک", "ar": "الاسم الأول", "en": "First name"},
    "create_khatm.display_label.PSEUDONYM": {"fa": "نام مؤسسه", "ar": "اسم المؤسسة", "en": "Institution"},
    "create_khatm.display_label.ANONYMOUS": {"fa": "ناشناس", "ar": "مجهول", "en": "Anonymous"},
    "create_khatm.tone_label.FRIENDLY": {"fa": "صمیمی", "ar": "ودّي", "en": "Friendly"},
    "create_khatm.tone_label.FORMAL": {"fa": "رسمی", "ar": "رسمي", "en": "Formal"},
    "create_khatm.tone_label.DEVOTIONAL": {"fa": "معنوی", "ar": "روحاني", "en": "Devotional"},
    "create_khatm.tone_label.SHORT": {"fa": "کوتاه", "ar": "مختصر", "en": "Short"},
    "create_khatm.content_mode_label.AUTO": {"fa": "خودکار", "ar": "تلقائي", "en": "Automatic"},
    "create_khatm.content_mode_label.PHOTO": {"fa": "فقط تصویر", "ar": "صورة فقط", "en": "Image only"},
    "create_khatm.content_mode_label.TEXT": {"fa": "فقط متن", "ar": "نص فقط", "en": "Text only"},
    "create_khatm.group_label.SALAWAT": {"fa": "صلوات", "ar": "صلوات", "en": "Salawat"},
    "create_khatm.group_label.DUA": {"fa": "دعا یا زیارت", "ar": "دعاء أو زيارة", "en": "Dua or Ziyarat"},
    "create_khatm.group_label.LAAN": {"fa": "لعن", "ar": "لعن", "en": "La'an"},
    "create_khatm.group_label.generic": {"fa": "ذکر شمارشی", "ar": "ذكر عدّي", "en": "Countable recitation"},
    "create_khatm.group_label.quran": {"fa": "قرآن", "ar": "القرآن", "en": "Quran"},
    "create_khatm.progress.header": {"fa": "📋 انتخاب‌های شما تا اینجا:", "ar": "📋 اختياراتك حتى الآن:", "en": "📋 Your choices so far:"},
    "create_khatm.progress.content": {"fa": "• نوع ختم: {value}", "ar": "• نوع الختمة: {value}", "en": "• Khatm type: {value}"},
    "create_khatm.progress.mode": {"fa": "• شیوه: {value}", "ar": "• النمط: {value}", "en": "• Mode: {value}"},
    "create_khatm.progress.niyyat": {"fa": "• نیت: {value}", "ar": "• النية: {value}", "en": "• Intention: {value}"},
    "create_khatm.progress.target": {"fa": "• هدف کل: {value}", "ar": "• الهدف الكلي: {value}", "en": "• Total goal: {value}"},
    "create_khatm.progress.visibility": {"fa": "• عضویت: {value}", "ar": "• الانضمام: {value}", "en": "• Membership: {value}"},
    "create_khatm.capacity_unlimited": {"fa": "نامحدود", "ar": "غير محدود", "en": "Unlimited"},
    "create_khatm.confirm.title": {"fa": "عنوان: {value}", "ar": "العنوان: {value}", "en": "Title: {value}"},
    "create_khatm.confirm.niyyat": {"fa": "نیت: {value}", "ar": "النية: {value}", "en": "Intention: {value}"},
    "create_khatm.confirm.welcome": {
        "fa": "پیام خوش‌آمد: {value}", "ar": "رسالة الترحيب: {value}", "en": "Welcome message: {value}",
    },
    "create_khatm.confirm.creator_display": {
        "fa": "نمایش نام سازنده: {value}", "ar": "عرض اسم المنشئ: {value}", "en": "Creator name display: {value}",
    },
    "create_khatm.confirm.mode": {"fa": "حالت: {value}", "ar": "الحالة: {value}", "en": "Mode: {value}"},
    "create_khatm.confirm.membership": {
        "fa": "عضویت: {value}", "ar": "العضوية: {value}", "en": "Membership: {value}",
    },
    "create_khatm.confirm.tone": {
        "fa": "لحن یادآوری: {value}", "ar": "أسلوب التذكير: {value}", "en": "Reminder tone: {value}",
    },
    "create_khatm.confirm.start_at": {
        "fa": "شروع: {value} به وقت تهران", "ar": "البدء: {value} بتوقيت طهران", "en": "Start: {value} Tehran time",
    },
    "create_khatm.confirm.start_now": {"fa": "شروع: همین حالا", "ar": "البدء: الآن", "en": "Start: right now"},
    "create_khatm.confirm.content_type": {
        "fa": "نوع محتوا: {value}", "ar": "نوع المحتوى: {value}", "en": "Content type: {value}",
    },
    "create_khatm.confirm.total_target": {
        "fa": "هدف کل: {amount} {unit}", "ar": "الهدف الكلي: {amount} {unit}", "en": "Total goal: {amount} {unit}",
    },
    "create_khatm.confirm.total_unlimited": {
        "fa": "هدف کل: نامحدود", "ar": "الهدف الكلي: غير محدود", "en": "Total goal: unlimited",
    },
    "create_khatm.want_other_lang_links": {
        "fa": "🌐 لینک عربی و انگلیسی هم می‌خواهم",
        "ar": "🌐 أريد روابط العربية والإنجليزية أيضاً",
        "en": "🌐 I also want the Arabic & English links",
    },
    "create_khatm.other_lang_hint": {
        "fa": "اگر مخاطب عرب‌زبان یا انگلیسی‌زبان هم دارید، لینک آن‌ها را هم بگیرید:",
        "ar": "إن كان لديك مدعوّون بالعربية أو الإنجليزية، احصل على روابطهم أيضاً:",
        "en": "If you also have Arabic- or English-speaking guests, get their links too:",
    },
    "create_khatm.no_other_lang_links": {
        "fa": "برای این دسته، بات عربی یا انگلیسی فعالی تنظیم نشده.",
        "ar": "لا يوجد بوت عربي أو إنجليزي مفعّل لهذه الفئة.",
        "en": "No active Arabic or English bot is configured for this category.",
    },
    "create_khatm.confirm.capacity": {
        "fa": "ظرفیت تعهدی: {value}", "ar": "سعة الالتزام: {value}", "en": "Commitment capacity: {value}",
    },
    "create_khatm.confirm.quran_content": {
        "fa": "نوع محتوا: ختم قرآن", "ar": "نوع المحتوى: ختمة القرآن", "en": "Content type: Quran khatm",
    },
    "create_khatm.confirm.edition": {"fa": "نسخه: {value}", "ar": "النسخة: {value}", "en": "Edition: {value}"},
    "create_khatm.confirm.delivery_format": {
        "fa": "فرمت ارسال: {value}", "ar": "صيغة الإرسال: {value}", "en": "Delivery format: {value}",
    },
    "create_khatm.confirm.deadline": {
        "fa": "مهلت روزانه: ساعت {hour}", "ar": "المهلة اليومية: الساعة {hour}", "en": "Daily deadline: {hour}:00",
    },
    "create_khatm.confirm.cost_line": {
        "fa": "\nهزینه ساخت: {amount} تومان (از کیف پولتون کم می‌شه)",
        "ar": "\nتكلفة الإنشاء: {amount} تومان (تُخصم من محفظتك)",
        "en": "\nCreation cost: {amount} toman (deducted from your wallet)",
    },
    "create_khatm.confirm.coupon_hint": {
        "fa": "اگر کد تخفیف دارید، دکمه «کد تخفیف دارم» را بزنید.",
        "ar": "إذا كان لديك رمز خصم، اضغط زر «لدي رمز خصم».",
        "en": "If you have a discount code, tap “I have a coupon”.",
    },
    "create_khatm.confirm.final_warning": {
        "fa": "\n✅ بعد از شروع هم می‌توانید از بخش «ختم‌های من» اطلاعات قابل‌ویرایش ختم را تغییر دهید. تایید می‌کنید؟",
        "ar": "\n⚠️ بعد التأكيد لا يمكن تغيير هذه الإعدادات. هل تؤكد؟",
        "en": "\n⚠️ After you confirm, these settings can no longer be changed. Confirm?",
    },
    "create_khatm.plan_unavailable": {
        "fa": "پلن فعلی شما اجازه ساخت ختم را ندارد.", "ar": "خطتك الحالية لا تسمح بإنشاء ختمة.",
        "en": "Your current plan does not allow creating a khatm.",
    },
    "create_khatm.plan_unavailable_support": {
        "fa": "پلن فعلی شما اجازه ساخت ختم را ندارد. لطفاً با پشتیبانی تماس بگیرید.",
        "ar": "خطتك الحالية لا تسمح بإنشاء ختمة. يرجى التواصل مع الدعم.",
        "en": "Your current plan does not allow creating a khatm. Please contact support.",
    },
    "create_khatm.coupon_free_khatm": {
        "fa": "ساخت این ختم رایگان است.", "ar": "إنشاء هذه الختمة مجاني.", "en": "Creating this khatm is free.",
    },
    "create_khatm.ask_coupon": {
        "fa": "🎟 لطفاً فقط خودِ کد تخفیف را بنویسید و بفرستید.\n\nمثال: KHATM20\n\nاگر کدی ندارید، دکمه «ادامه بدون کد» را بزنید.",
        "ar": "🎟 يرجى كتابة رمز الخصم فقط وإرساله.\n\nمثال: KHATM20\n\nإذا لم يكن لديك رمز، اضغط زر «المتابعة بدون رمز».",
        "en": "🎟 Please type and send just the coupon code.\n\nExample: KHATM20\n\nIf you don't have one, tap “Continue without a code”.",
    },
    "create_khatm.coupon_empty": {
        "fa": "کد خالی بود. لطفاً فقط خودِ کد تخفیف را بفرستید.",
        "ar": "الرمز كان فارغاً. يرجى إرسال رمز الخصم فقط.",
        "en": "The code was empty. Please send only the coupon code.",
    },
    "create_khatm.coupon_not_needed": {
        "fa": "ساخت این ختم رایگان است و نیازی به کد تخفیف ندارد.",
        "ar": "إنشاء هذه الختمة مجاني ولا يحتاج إلى رمز خصم.",
        "en": "Creating this khatm is free and doesn't need a coupon code.",
    },
    "create_khatm.coupon_invalid": {
        "fa": "این کد معتبر یا فعال نیست، حداقل خریدش رعایت نشده، یا ظرفیت استفاده‌اش تمام شده است.\n\nکد دیگری بفرستید یا دکمه «ادامه بدون کد» را بزنید.",
        "ar": "هذا الرمز غير صالح أو غير مفعّل، أو لم يتحقق الحد الأدنى للشراء، أو انتهت سعة استخدامه.\n\nأرسل رمزاً آخر أو اضغط زر «المتابعة بدون رمز».",
        "en": "This code is invalid or inactive, doesn't meet the minimum purchase, or has run out of uses.\n\nSend another code or tap “Continue without a code”.",
    },
    "create_khatm.coupon_accepted": {
        "fa": "کد تخفیف پذیرفته شد ✅\n\nهزینه اصلی: {gross} تومان\nتخفیف: {discount} تومان\nمبلغ نهایی: {net} تومان\n\nحالا فقط دکمهٔ تأیید را بزنید.",
        "ar": "تم قبول رمز الخصم ✅\n\nالتكلفة الأصلية: {gross} تومان\nالخصم: {discount} تومان\nالمبلغ النهائي: {net} تومان\n\nالآن فقط اضغط زر التأكيد.",
        "en": "Coupon accepted ✅\n\nOriginal cost: {gross} toman\nDiscount: {discount} toman\nFinal amount: {net} toman\n\nNow just tap Confirm.",
    },
    "create_khatm.ask_coupon_command": {
        "fa": "لطفاً فقط خودِ کد تخفیف را بنویسید و بفرستید.",
        "ar": "يرجى كتابة رمز الخصم فقط وإرساله.",
        "en": "Please type and send just the coupon code.",
    },
    "create_khatm.cancelled": {
        "fa": "ساخت ختم لغو شد.", "ar": "تم إلغاء إنشاء الختمة.", "en": "Khatm creation was cancelled.",
    },
    "create_khatm.insufficient_funds": {
        "fa": "موجودی کیف پولتون کافی نیست (هزینه ساخت: {price} تومان). لطفاً اول کیف پولتون رو شارژ کنید.",
        "ar": "رصيد محفظتك غير كافٍ (تكلفة الإنشاء: {price} تومان). يرجى شحن محفظتك أولاً.",
        "en": "Your wallet balance isn't enough (creation cost: {price} toman). Please top up your wallet first.",
    },
    "create_khatm.coupon_expired_at_confirm": {
        "fa": "کد تخفیف دیگر قابل استفاده نیست. دکمه «کد تخفیف دارم» را بزنید و کد دیگری وارد کنید؛ یا همین حالا با قیمت کامل تأیید کنید.",
        "ar": "لم يعد رمز الخصم صالحاً. اضغط زر «لدي رمز خصم» وأدخل رمزاً آخر، أو أكّد الآن بالسعر الكامل.",
        "en": "The coupon can no longer be used. Tap “I have a coupon” to enter another one, or confirm now at the full price.",
    },
    "create_khatm.success": {
        "fa": "🎉 ختم «{title}» ساخته و فعال شد!\n\nلینک دعوت:\n{invite_line}{landing_line}\n\nاین رو برای شرکت‌کننده‌ها بفرستید.",
        "ar": "🎉 تم إنشاء وتفعيل ختمة «{title}»!\n\nرابط الدعوة:\n{invite_line}{landing_line}\n\nأرسل هذا للمشاركين.",
        "en": "🎉 The khatm “{title}” was created and activated!\n\nInvite link:\n{invite_line}{landing_line}\n\nSend this to participants.",
    },
    "create_khatm.success_creator": {
        "fa": "🎉 ختم «{title}» با موفقیت ساخته و فعال شد!\n\nپست زیر را برای مخاطبین، گروه‌ها یا کانال‌های خود ارسال کنید 👇",
        "ar": "🎉 تم إنشاء وتفعيل ختمة «{title}» بنجاح!\n\nأرسل المنشور أدناه إلى جهات اتصالك أو مجموعاتك أو قنواتك 👇",
        "en": "🎉 The khatm “{title}” was successfully created and activated!\n\nShare the post below with your contacts, groups, or channels 👇",
    },
    "create_khatm.landing_line": {
        "fa": "\n\nصفحه معرفی ختم:\n{url}", "ar": "\n\nصفحة تعريف الختمة:\n{url}", "en": "\n\nKhatm landing page:\n{url}",
    },

    # --- settings_menu.py (2026-09-20) ---
    "settings.home_text": {
        "fa": "⚙️ تنظیمات\n\nهر مورد را با زدن دکمه‌اش تغییر بده:",
        "ar": "⚙️ الإعدادات\n\nغيّر أي عنصر بالضغط على زره:",
        "en": "⚙️ Settings\n\nChange any item by tapping its button:",
    },
    "settings.choose_language": {
        "fa": "🌐 زبان بات را انتخاب کن:", "ar": "🌐 اختر لغة البوت:", "en": "🌐 Choose the bot's language:",
    },
    "settings.language_saved": {"fa": "زبان تغییر کرد ✅", "ar": "تم تغيير اللغة ✅", "en": "Language changed ✅"},
    "settings.choose_font": {
        "fa": "🔤 اندازه متن را انتخاب کن:", "ar": "🔤 اختر حجم الخط:", "en": "🔤 Choose the text size:",
    },
    "settings.font_saved": {"fa": "اندازه متن تغییر کرد ✅", "ar": "تم تغيير حجم الخط ✅", "en": "Text size changed ✅"},
    "settings.choose_reciter": {
        "fa": "🎙 قاری مورد علاقه‌ات را انتخاب کن:", "ar": "🎙 اختر قارئك المفضل:", "en": "🎙 Choose your favorite reciter:",
    },
    "settings.reciter_saved": {"fa": "قاری ذخیره شد ✅", "ar": "تم حفظ القارئ ✅", "en": "Reciter saved ✅"},
    "settings.content_menu": {
        "fa": "📖 ترجمه و تفسیر:", "ar": "📖 الترجمة والتفسير:", "en": "📖 Translation and commentary:",
    },
    "settings.saved": {"fa": "ذخیره شد ✅", "ar": "تم الحفظ ✅", "en": "Saved ✅"},
    "settings.choose_reminder_hour": {
        "fa": "⏰ ساعت یادآوری تعهدهای روزانه‌ات را انتخاب کن:",
        "ar": "⏰ اختر ساعة تذكير التزاماتك اليومية:",
        "en": "⏰ Choose the reminder hour for your daily commitments:",
    },
    "settings.reminder_saved": {"fa": "یادآوری تنظیم شد ✅", "ar": "تم ضبط التذكير ✅", "en": "Reminder set ✅"},
    "settings.digest_menu": {"fa": "🗞 خلاصه روزانه:", "ar": "🗞 الملخص اليومي:", "en": "🗞 Daily digest:"},
    "settings.sms_menu_title": {
        "fa": "📩 پیامک یادآوری\n\nپیامک یادآوری فقط با خرید اشتراک فعال می‌شه.\n",
        "ar": "📩 رسائل التذكير\n\nتُفعَّل رسائل التذكير فقط بشراء اشتراك.\n",
        "en": "📩 SMS reminders\n\nSMS reminders only turn on after you buy a subscription.\n",
    },
    "settings.sms_active": {
        "fa": "✅ اشتراک شما فعاله، تا تاریخ {date} (میلادی).\n",
        "ar": "✅ اشتراكك مفعّل حتى تاريخ {date} (ميلادي).\n",
        "en": "✅ Your subscription is active until {date} (Gregorian).\n",
    },
    "settings.sms_inactive": {
        "fa": "❌ الان اشتراک فعالی ندارید.\n", "ar": "❌ ليس لديك اشتراك فعال الآن.\n",
        "en": "❌ You don't have an active subscription right now.\n",
    },
    "settings.sms_buy_prompt": {
        "fa": "\nبرای خرید یا تمدید، یکی از گزینه‌ها رو انتخاب کنید:",
        "ar": "\nللشراء أو التجديد، اختر أحد الخيارات:",
        "en": "\nTo buy or renew, choose one of the options:",
    },
    "settings.sms_off": {"fa": "پیامک خاموش شد ✅", "ar": "تم إيقاف الرسائل ✅", "en": "SMS turned off ✅"},
    "settings.sms_option_invalid": {
        "fa": "گزینهٔ اشتراک معتبر نیست.", "ar": "خيار الاشتراك غير صالح.", "en": "That subscription option isn't valid.",
    },
    "settings.sms_phone_required": {
        "fa": "ابتدا شماره موبایل را در پروفایل ثبت کن",
        "ar": "أولاً سجّل رقم جوالك في الملف الشخصي",
        "en": "First register your phone number in your profile",
    },
    "settings.sms_insufficient_funds": {
        "fa": "موجودی کیف پولتون کافی نیست؛ اول کیف پول رو شارژ کنید.",
        "ar": "رصيد محفظتك غير كافٍ؛ اشحن محفظتك أولاً.",
        "en": "Your wallet balance isn't enough; please top up your wallet first.",
    },
    "settings.sms_plan_unavailable": {
        "fa": "این گزینه دیگر در دسترس نیست.", "ar": "هذا الخيار لم يعد متاحاً.", "en": "This option is no longer available.",
    },
    "settings.sms_activated": {
        "fa": "اشتراک تا {date} فعال شد ✅", "ar": "تم تفعيل الاشتراك حتى {date} ✅", "en": "Subscription activated until {date} ✅",
    },
    "settings.choose_timezone": {
        "fa": "🕒 منطقه زمانی خودت را انتخاب کن:", "ar": "🕒 اختر منطقتك الزمنية:", "en": "🕒 Choose your timezone:",
    },
    "settings.timezone_saved": {
        "fa": "منطقه زمانی ذخیره شد ✅", "ar": "تم حفظ المنطقة الزمنية ✅", "en": "Timezone saved ✅",
    },
    "settings.button.back": {
        "fa": "🔙 بازگشت به تنظیمات", "ar": "🔙 الرجوع إلى الإعدادات", "en": "🔙 Back to settings",
    },
    "settings.button.audio_off": {
        "fa": "🔊 صوت قرآن روشن است — خاموش کردن", "ar": "🔊 صوت القرآن مفعّل — إيقاف", "en": "🔊 Quran audio is on — turn off",
    },
    "settings.button.audio_on": {
        "fa": "🔇 صوت قرآن خاموش است — روشن کردن", "ar": "🔇 صوت القرآن متوقف — تشغيل", "en": "🔇 Quran audio is off — turn on",
    },
    "settings.button.language": {"fa": "🌐 زبان", "ar": "🌐 اللغة", "en": "🌐 Language"},
    "settings.button.font": {"fa": "🔤 اندازه متن", "ar": "🔤 حجم الخط", "en": "🔤 Text size"},
    "settings.button.reciter": {"fa": "🎙 قاری", "ar": "🎙 القارئ", "en": "🎙 Reciter"},
    "settings.button.content": {"fa": "📖 ترجمه و تفسیر", "ar": "📖 الترجمة والتفسير", "en": "📖 Translation & commentary"},
    "settings.button.reminder": {"fa": "⏰ یادآوری", "ar": "⏰ التذكير", "en": "⏰ Reminder"},
    "settings.button.digest": {"fa": "🗞 خلاصه روزانه", "ar": "🗞 الملخص اليومي", "en": "🗞 Daily digest"},
    "settings.button.font_normal": {"fa": "معمولی", "ar": "عادي", "en": "Normal"},
    "settings.button.font_large": {"fa": "درشت", "ar": "كبير", "en": "Large"},
    "settings.label.translation": {"fa": "ترجمه", "ar": "الترجمة", "en": "Translation"},
    "settings.label.tafsir": {"fa": "تفسیر", "ar": "التفسير", "en": "Commentary"},
    "settings.button.turn_off": {"fa": "خاموش کردن", "ar": "إيقاف", "en": "Turn off"},
    "settings.button.turn_on": {"fa": "روشن کردن", "ar": "تشغيل", "en": "Turn on"},
    "settings.button.reminder_off": {"fa": "🔕 خاموش", "ar": "🔕 إيقاف", "en": "🔕 Off"},
    "settings.button.on_active": {"fa": "✅ روشن", "ar": "✅ مفعّل", "en": "✅ On"},
    "settings.button.off_active": {"fa": "✅ خاموش", "ar": "✅ معطّل", "en": "✅ Off"},
    "settings.button.sms_buy": {
        "fa": "🛒 {months} ماهه — {price} تومان", "ar": "🛒 {months} أشهر — {price} تومان", "en": "🛒 {months} months — {price} toman",
    },
    "settings.button.sms_off": {"fa": "خاموش کردن پیامک", "ar": "إيقاف الرسائل", "en": "Turn off SMS"},
    "settings.button.sms_menu": {"fa": "📩 پیامک یادآوری", "ar": "📩 رسائل التذكير", "en": "📩 SMS reminders"},
    "settings.button.timezone": {"fa": "🕒 منطقه زمانی", "ar": "🕒 المنطقة الزمنية", "en": "🕒 Timezone"},
    "settings.button.profile": {
        "fa": "✏️ ویرایش مشخصات من", "ar": "✏️ تعديل بياناتي", "en": "✏️ Edit my profile",
    },
    "settings.button.change_phone": {"fa": "📱 تغییر شماره", "ar": "📱 تغيير الرقم", "en": "📱 Change phone number"},
    "settings.button.link_account": {
        "fa": "🔗 اتصال حساب قبلی", "ar": "🔗 ربط حساب سابق", "en": "🔗 Link a previous account",
    },
    "settings.button.creator_panel": {
        "fa": "🎛 ورود به پنل سازنده", "ar": "🎛 الدخول إلى لوحة المنشئ", "en": "🎛 Open creator panel",
    },

    # --- my_khatms.py: member-facing list entry point (2026-09-20) ---
    "my_khatms.bucket.active": {"fa": "فعال", "ar": "نشطة", "en": "Active"},
    "my_khatms.bucket.upcoming": {"fa": "آینده", "ar": "قادمة", "en": "Upcoming"},
    "my_khatms.bucket.finished": {"fa": "تمام‌شده", "ar": "منتهية", "en": "Finished"},
    "my_khatms.created_line": {"fa": "— {title} ({status})", "ar": "— {title} ({status})", "en": "— {title} ({status})"},
    "my_khatms.open_line": {
        "fa": "— [{bucket}] {title}: {total} ثبت شده", "ar": "— [{bucket}] {title}: {total} مسجَّل",
        "en": "— [{bucket}] {title}: {total} logged",
    },
    "my_khatms.waiting_note": {"fa": " (در لیست انتظار)", "ar": " (في قائمة الانتظار)", "en": " (on the waiting list)"},
    "my_khatms.progress_line": {
        "fa": "— [{bucket}] {title}{waiting_note}: پیشرفت گروهی {done}/{total}",
        "ar": "— [{bucket}] {title}{waiting_note}: تقدم المجموعة {done}/{total}",
        "en": "— [{bucket}] {title}{waiting_note}: group progress {done}/{total}",
    },
    "my_khatms.empty": {
        "fa": "هنوز هیچ ختمی نساختید و عضو هیچ ختمی هم نیستید.\nبرای شروع «➕ ساخت ختم جدید» رو بزنید.",
        "ar": "لم تُنشئ أي ختمة بعد ولست عضواً في أي ختمة.\nللبدء اضغط «➕ إنشاء ختمة جديدة».",
        "en": "You haven't created any khatm yet and aren't a member of one either.\nTap “➕ Create a new khatm” to get started.",
    },

    # --- my_khatms.py: hierarchical redesign (BACKLOG.md §18, 2026-09-21)
    # — three top-level branches (created/joined/finished), each split by
    # content type (Quran/Salawat/Dua/La'an), instead of one long text list ---
    "my_khatms.root.header": {
        "fa": "🕋 ختم‌های من — کدوم بخش رو می‌خواید ببینید؟",
        "ar": "🕋 ختماتي — أي قسم تريد أن ترى؟",
        "en": "🕋 My khatms — which section would you like to see?",
    },
    "my_khatms.root.button.created": {
        "fa": "🌱 ساخته‌ام ({count})", "ar": "🌱 التي أنشأتها ({count})", "en": "🌱 I created ({count})",
    },
    "my_khatms.root.button.joined": {
        "fa": "🤝 عضوشونم ({count})", "ar": "🤝 التي أنا عضو فيها ({count})", "en": "🤝 I've joined ({count})",
    },
    "my_khatms.root.button.finished": {
        "fa": "✅ تمام‌شده ({count})", "ar": "✅ المنتهية ({count})", "en": "✅ Finished ({count})",
    },
    "my_khatms.branch.title.created": {
        "fa": "🌱 ختم‌هایی که ساختید", "ar": "🌱 الختمات التي أنشأتها", "en": "🌱 Khatms you created",
    },
    "my_khatms.branch.title.joined": {
        "fa": "🤝 ختم‌هایی که عضوشون هستید", "ar": "🤝 الختمات التي أنت عضو فيها", "en": "🤝 Khatms you've joined",
    },
    "my_khatms.branch.title.finished": {
        "fa": "✅ ختم‌های تمام‌شده", "ar": "✅ الختمات المنتهية", "en": "✅ Finished khatms",
    },
    "my_khatms.branch.choose_category": {
        "fa": "کدوم دسته رو می‌خواید ببینید؟", "ar": "أي فئة تريد أن ترى؟", "en": "Which category would you like to see?",
    },
    "my_khatms.branch.empty": {
        "fa": "این بخش هنوز خالیه.", "ar": "هذا القسم فارغ حالياً.", "en": "This section is empty for now.",
    },
    "my_khatms.category.quran": {"fa": "📖 قرآن", "ar": "📖 القرآن", "en": "📖 Quran"},
    "my_khatms.category.salawat": {"fa": "🕊 صلوات", "ar": "🕊 الصلوات", "en": "🕊 Salawat"},
    "my_khatms.category.dua": {"fa": "🤲 دعا و زیارت", "ar": "🤲 الدعاء والزيارة", "en": "🤲 Dua & Ziyarat"},
    "my_khatms.category.laan": {"fa": "⚔️ لعن", "ar": "⚔️ اللعن", "en": "⚔️ La'an"},
    "my_khatms.button.back": {"fa": "🔙 بازگشت", "ar": "🔙 رجوع", "en": "🔙 Back"},
    # --- portions.py (2026-09-20) ---
    "portions.unit.page": {"fa": "صفحه", "ar": "صفحة", "en": "page"},
    "portions.button.contribute": {"fa": "✅ انجام سهم", "ar": "✅ إنجاز الحصة", "en": "✅ Complete share"},
    "portions.button.show_content": {
        "fa": "📖 نمایش محتوای سهم", "ar": "📖 عرض محتوى الحصة", "en": "📖 Show portion content",
    },
    "portions.button.done": {"fa": "✅ قرائت بخش فوق انجام شد", "ar": "✅ أنجزت", "en": "✅ I did it"},
    "portions.button.done.quran": {"fa": "✅ قرائت صفحات انجام شد", "ar": "✅ تمّت القراءة", "en": "✅ Pages Read"},
    "portions.button.done.salawat": {"fa": "✅ صلوات‌ها فرستاده شد", "ar": "✅ تمّت الصلاة", "en": "✅ Salawat Sent"},
    "portions.button.done.dua": {"fa": "✅ قرائت دعا / زیارت انجام شد", "ar": "✅ تمّت القراءة", "en": "✅ Dua Recited"},
    "portions.button.done.laan": {"fa": "✅ ذکر لعن انجام شد", "ar": "✅ تمّ الذكر", "en": "✅ La'an Recited"},
    "portions.button.done.khutbah": {"fa": "✅ استماع / قرائت بخش انجام شد", "ar": "✅ تم الاستماع / القراءة", "en": "✅ Khutbah Completed"},
    "portions.button.snooze": {"fa": "⏰ تعویق یادآوری", "ar": "⏰ تأجيل التذكير", "en": "⏰ Snooze reminder"},
    "portions.button.undo": {
        "fa": "↩️ لغو آخرین ثبت (تا ۵ دقیقه)", "ar": "↩️ تراجع عن آخر تسجيل (خلال ۵ دقائق)",
        "en": "↩️ Undo last entry (within 5 minutes)",
    },
    "portions.button.log_commitment_part": {
        "fa": "➕ ثبت بخشی از تعهد", "ar": "➕ تسجيل جزء من الالتزام", "en": "➕ Log part of your commitment",
    },
    "portions.unit.time": {"fa": "بار", "ar": "مرة", "en": "time"},
    "portions.snooze_not_allowed": {
        "fa": "تعویق یادآوری برای این ختم فعال نیست.", "ar": "تأجيل التذكير غير مفعّل لهذه الختمة.",
        "en": "Reminder snoozing isn't enabled for this khatm.",
    },
    "portions.ask_snooze_duration": {
        "fa": "یادآوری این سهم را برای چه مدتی عقب بیندازیم؟", "ar": "كم من الوقت نؤجل تذكير هذه الحصة؟",
        "en": "How long should we delay the reminder for this portion?",
    },
    "portions.not_a_member": {"fa": "شما عضو این ختم نیستید.", "ar": "لست عضواً في هذه الختمة.", "en": "You aren't a member of this khatm."},
    "portions.snooze_label.30": {"fa": "۳۰ دقیقه", "ar": "۳۰ دقيقة", "en": "30 minutes"},
    "portions.snooze_label.60": {"fa": "۱ ساعت", "ar": "ساعة واحدة", "en": "1 hour"},
    "portions.snooze_label.180": {"fa": "۳ ساعت", "ar": "۳ ساعات", "en": "3 hours"},
    "portions.snooze_label.custom": {"fa": "🗓 زمان دلخواه", "ar": "🗓 وقت مخصص", "en": "🗓 Custom time"},
    "portions.snoozed": {
        "fa": "یادآوری این ختم برای {label} به تعویق افتاد ✅", "ar": "تم تأجيل تذكير هذه الختمة لمدة {label} ✅",
        "en": "This khatm's reminder was delayed by {label} ✅",
    },
    "portions.ask_custom_snooze_time": {
        "fa": "چند ساعت می‌خواهید یادآوری به تعویق بیفتد؟ (مثلاً برای دو ساعت بفرستید: 2)\nیا تاریخ دقیق: YYYY-MM-DD HH:MM",
        "ar": "كم ساعة تريد تأجيل التذكير؟ (مثلاً لساعتين أرسل: 2)\nأو تاريخ دقيق: YYYY-MM-DD HH:MM",
        "en": "How many hours do you want to delay the reminder? (e.g., for two hours, send: 2)\nOr exact date: YYYY-MM-DD HH:MM",
    },
    "portions.time_format_invalid": {
        "fa": "فرمت زمان درست نیست. لطفاً یک عدد (مثل 2) یا تاریخ دقیق (مثل 2026-10-01 18:30) بفرستید.", "ar": "صيغة الوقت غير صحيحة. يرجى إرسال رقم (مثل 2) أو تاريخ دقيق (مثل 2026-10-01 18:30).",
        "en": "Invalid time format. Please send a number (like 2) or an exact date (like 2026-10-01 18:30).",
    },
    "portions.khatm_inactive_or_not_member": {
        "fa": "این ختم فعال نیست یا تعویق یادآوری برای آن خاموش شده است.",
        "ar": "هذه الختمة غير نشطة أو تم إيقاف تأجيل التذكير لها.",
        "en": "This khatm isn't active, or reminder snoozing is turned off for it.",
    },
    "portions.snooze_must_be_future": {
        "fa": "زمان پایان تعویق باید در آینده باشد.", "ar": "يجب أن يكون وقت انتهاء التأجيل في المستقبل.",
        "en": "The snooze end time must be in the future.",
    },
    "portions.snooze_custom_saved": {
        "fa": "تعویق یادآوری تا زمان انتخاب‌شده ثبت شد ✅", "ar": "تم تسجيل تأجيل التذكير حتى الوقت المحدد ✅",
        "en": "The reminder snooze was recorded until the chosen time ✅",
    },
    "portions.no_active_quran_portion": {
        "fa": "سهم قرآن فعالی برای شما پیدا نشد.", "ar": "لم يتم العثور على حصة قرآن نشطة لك.",
        "en": "No active Quran portion was found for you.",
    },
    "portions.no_active_portion_to_show": {
        "fa": "سهم فعالی برای نمایش محتوا پیدا نشد.", "ar": "لم يتم العثور على حصة نشطة لعرض المحتوى.",
        "en": "No active portion was found to show content for.",
    },
    "portions.content_not_registered": {
        "fa": "محتوای صفحات {start} تا {end} هنوز در کتابخانه ثبت نشده است.",
        "ar": "لم يُسجَّل بعد محتوى الصفحات من {start} إلى {end} في المكتبة.",
        "en": "The content for pages {start} to {end} hasn't been registered in the library yet.",
    },
    "portions.your_portion_header": {
        "fa": "📖 سهم شما: صفحه‌های {start} تا {end}\n\n"
        "ابتدا تصویر صفحه‌ها فرستاده می‌شود. اگر صوت را در تنظیمات روشن کرده باشید، "
        "تلاوت پرهیزگار هم بعد از تصویرها می‌آید.",
        "ar": "📖 حصتك: الصفحات من {start} إلى {end}\n\n"
        "تُرسل صور الصفحات أولاً. إذا فعّلت الصوت في الإعدادات، تأتي التلاوة بعد الصور.",
        "en": "📖 Your portion: pages {start} to {end}\n\n"
        "Page images are sent first. If you turned on audio in settings, the recitation follows the images.",
    },
    "portions.content_send_failed": {
        "fa": "ارسال فایل‌های قرآن انجام نشد. مدیر باید ربات را عضو کانال منبع کند یا دسترسی آن را بررسی کند. "
        "سهم شما تغییری نکرده است؛ کمی بعد دوباره «نمایش محتوای سهم» را بزنید.",
        "ar": "تعذّر إرسال ملفات القرآن. يجب على المدير إضافة البوت لقناة المصدر أو التحقق من صلاحياته. "
        "لم تتغيّر حصتك؛ حاول «عرض محتوى الحصة» مرة أخرى بعد قليل.",
        "en": "Sending the Quran files failed. An admin needs to add the bot to the source channel or check its access. "
        "Your portion hasn't changed; try “Show portion content” again shortly.",
    },
    "portions.no_portion_to_complete": {
        "fa": "سهمی برای تکمیل پیدا نشد.", "ar": "لم يتم العثور على حصة لإكمالها.", "en": "No portion was found to complete.",
    },
    "portions.plan_completed": {
        "fa": "🎉 هدف کلی ختم تکمیل شد و ختم به پایان رسید. خدا قبول کنه 🤍\n"
        "پیام پایان بعد از مهلت ۵ دقیقه‌ای لغو ثبت، برای همراهان ارسال می‌شود.",
        "ar": "🎉 اكتمل الهدف الكلي للختمة وانتهت. تقبّل الله 🤍\n"
        "ستُرسل رسالة النهاية للمشاركين بعد مهلة ۵ دقائق لإلغاء التسجيل.",
        "en": "🎉 The khatm's overall goal was completed and it has ended. May it be accepted 🤍\n"
        "The completion message will be sent to members after the 5-minute undo window.",
    },
    "portions.page_done_next_tomorrow": {
        "fa": "✅ صفحات {start} تا {end} خوانده شد.\n\n"
        "قرائت شما ثبت شد و در ثواب این ختم شریک شدید. خدا از شما قبول کند 🤍\n\n"
        "سهم فردا به‌طور خودکار سر ساعت یادآوری‌تون براتون ارسال می‌شه.{invite_line}",
        "ar": "✅ تمت قراءة الصفحات من {start} إلى {end}.\n\n"
        "تم تسجيل قراءتك وشاركت في ثواب هذه الختمة. تقبّل الله منك 🤍\n\n"
        "ستصلك حصة الغد تلقائياً في موعد تذكيرك.{invite_line}",
        "en": "✅ Pages {start}–{end} recorded.\n\n"
        "Your recitation has been logged — may it be accepted 🤍\n\n"
        "Tomorrow's portion will arrive automatically at your reminder time.{invite_line}",
    },
    "portions.personal_portion_done": {
        "fa": "🎉 تبریک! سهم شخصی شما در این ختم به پایان رسید. خدا قبول کنه 🤍{invite_line}",
        "ar": "🎉 مبروك! انتهت حصتك الشخصية في هذه الختمة. تقبّل الله 🤍{invite_line}",
        "en": "🎉 Congratulations! Your personal portion in this khatm is complete. May it be accepted 🤍{invite_line}",
    },
    "portions.undo_not_found": {
        "fa": "این ثبت پیدا نشد.", "ar": "لم يتم العثور على هذا التسجيل.", "en": "This record wasn't found.",
    },
    "portions.undo_not_yours": {
        "fa": "این سهم متعلق به شما نیست.", "ar": "هذه الحصة ليست لك.", "en": "This portion isn't yours.",
    },
    "portions.undo_expired": {
        "fa": "مهلت لغو گذشته یا این ثبت دیگر قابل برگشت نیست.",
        "ar": "انتهت مهلة الإلغاء أو لم يعد هذا التسجيل قابلاً للتراجع.",
        "en": "The undo window has passed, or this record can no longer be reverted.",
    },
    "portions.undo_done": {
        "fa": "آخرین ثبت لغو شد؛ سهم دوباره فعال شد ✅", "ar": "تم إلغاء آخر تسجيل؛ الحصة نشطة مجدداً ✅",
        "en": "The last record was undone; the portion is active again ✅",
    },
    "portions.ask_open_amount": {
        "fa": "چند {unit} انجام دادید؟ فقط عدد بفرستید (مثلاً 100):",
        "ar": "كم {unit} أنجزت؟ أرسل رقماً فقط (مثلاً 100):",
        "en": "How many {unit} did you complete? Send a number only (e.g. 100):",
    },
    "portions.ask_open_amount_quran": {
        "fa": "چند صفحه خواندید؟ عدد (مثلاً 10) یا بازه (مثلاً 20 تا 31) بفرستید:",
        "ar": "كم صفحة قرأت؟ أرسل عدداً (مثلاً 10) أو نطاقاً (مثلاً 20 إلى 31):",
        "en": "How many pages did you read? Send a number (e.g. 10) or range (e.g. 20 to 31):",
    },
    "portions.ask_commitment_amount": {
        "fa": "چند بار از تعهدتون رو انجام دادید؟ فقط عدد بفرستید (مثلاً 300):",
        "ar": "كم مرة أنجزت من التزامك؟ أرسل رقماً فقط (مثلاً 300):",
        "en": "How many times did you complete from your pledge? Send a number only (e.g. 300):",
    },
    "portions.positive_number_required": {
        "fa": "لطفاً فقط یک عدد بزرگ‌تر از صفر بفرستید.", "ar": "يرجى إرسال رقم أكبر من صفر فقط.",
        "en": "Please send only a number greater than zero.",
    },
    "portions.no_capacity_left": {
        "fa": "ظرفیت کافی باقی نمانده است.",
        "ar": "سعة غير كافية.",
        "en": "Not enough capacity."
    },
    "portions.khatm_not_active": {
        "fa": "این ختم دیگر فعال نیست.", "ar": "هذه الختمة لم تعد نشطة.", "en": "This khatm is no longer active.",
    },
    "portions.no_active_commitment": {
        "fa": "تعهد فعالی برای ثبت پیدا نشد.", "ar": "لم يتم العثور على التزام نشط للتسجيل.",
        "en": "No active pledge was found to log against.",
    },
    "portions.commitment_recorded": {
        "fa": "✅ {counted} مرتبه از ذکر شما ثبت شد.\nخداوند از شما بپذیرد و شما را در ثواب این ختم شریک بگرداند 🤍",
        "ar": "✅ تم تسجيل {counted} مرة من ذكرك.\nتقبّل الله منك وأشركك في ثواب هذه الختمة 🤍",
        "en": "✅ {counted} of your recitations were recorded.\nMay Allah accept it and make you a partner in the reward of this khatm 🤍",
    },
    "portions.commitment_progress": {
        "fa": "پیشرفت تعهد شخصی: {completed} از {target}", "ar": "تقدم الالتزام الشخصي: {completed} من {target}",
        "en": "Your personal pledge progress: {completed} of {target}",
    },
    "portions.commitment_surplus": {
        "fa": "{surplus} بار به‌عنوان مشارکت مازاد شما ثبت شد 🌱",
        "ar": "تم تسجيل {surplus} مرة كمشاركة إضافية منك 🌱",
        "en": "{surplus} extra times were logged as your surplus contribution 🌱",
    },
    "portions.personal_commitment_done": {
        "fa": "\n\n🎉 تعهد شما به‌طور کامل ادا شد. زحمت و همراهی شما در این ختم مایهٔ دل‌گرمی است؛ خداوند این عبادت را از شما بپذیرد 🤍",
        "ar": "\n\n🎉 لقد أدّيت التزامك كاملاً. جهدك ومرافقتك في هذه الختمة مبعث سرور؛ تقبّل الله منك هذه العبادة 🤍",
        "en": "\n\n🎉 You have fulfilled your pledge in full. Your effort and companionship in this khatm are heartwarming; may Allah accept this worship from you 🤍",
    },
    "portions.open_recorded": {
        "fa": "{amount} {unit} ثبت شد ✅", "ar": "تم تسجيل {amount} {unit} ✅", "en": "{amount} {unit} recorded ✅",
    },

    # --- portions.py: open/waitlisted Quran reading setup (owner request,
    # 2026-09-21) — a non-committed Quran reader picks a daily page count
    # and delivery hour once; the bot then actually sends that many real
    # pages (image/audio/text) every day, instead of just logging a bare
    # number with nothing sent. ---
    "portions.open_quran.setup_ask_pages_per_day": {
        "fa": "قبل از شروع، یک سؤال کوتاه 🌱\n\nروزی چند صفحه از قرآن دوست دارید بخونید؟ فقط عدد رو بفرستید (مثلاً 5):",
        "ar": "قبل البدء، سؤال قصير 🌱\n\nكم صفحة من القرآن تحب أن تقرأ يومياً؟ أرسل رقماً فقط (مثلاً 5):",
        "en": "One quick question before we start 🌱\n\nHow many Quran pages would you like to read each day? Send a number only (e.g. 5):",
    },
    "portions.open_quran.pages_per_day_invalid": {
        "fa": "یک عدد مثبت بفرستید، مثلاً 5.", "ar": "أرسل رقماً موجباً، مثلاً 5.", "en": "Please send a positive number, like 5.",
    },
    "portions.open_quran.setup_ask_hour": {
        "fa": "چه ساعتی (به وقت خودتون) دوست دارید صفحات هر روز براتون فرستاده بشه؟ یکی از دکمه‌ها را بزنید، یا ساعت دقیق را بنویسید (مثلاً 9 یا 14:27):",
        "ar": "في أي ساعة (بتوقيتك) تحب أن تصلك الصفحات كل يوم؟ اضغط أحد الأزرار أو اكتب الوقت بدقة (مثلاً 9 أو 14:27):",
        "en": "What time (your own time) would you like the pages sent each day? Tap a button, or type an exact time (e.g. 9 or 14:27):",
    },
    "portions.open_quran.hour_invalid": {
        "fa": "یک ساعت معتبر بفرستید؛ مثلاً 9 یا 14:27.", "ar": "أرسل وقتاً صحيحاً؛ مثلاً 9 أو 14:27.",
        "en": "Please send a valid time, like 9 or 14:27.",
    },
    "portions.open_quran.setup_done": {
        "fa": "تنظیم شد ✅ هر روز ساعت {hour} به وقت خودتون، {pages_per_day} صفحه از قرآن براتون فرستاده می‌شه. اولین صفحات هم در همین ساعت می‌رسه 🌱",
        "ar": "تم الإعداد ✅ كل يوم الساعة {hour} بتوقيتك ستصلك {pages_per_day} صفحة من القرآن. وستصل الصفحات الأولى في هذا الموعد 🌱",
        "en": "All set ✅ Every day at {hour} your time, you'll receive {pages_per_day} Quran pages. The first pages will arrive at that time too 🌱",
    },
    "portions.open_quran.already_finished": {
        "fa": "🎉 شما همهٔ صفحات این ختم قرآن رو خوندید! چیز دیگه‌ای برای فرستادن نمونده. خدا قبول کنه 🤍",
        "ar": "🎉 لقد قرأت كل صفحات هذه الختمة! لم يتبقَّ شيء لإرساله. تقبّل الله 🤍",
        "en": "🎉 You've read every page of this khatm's Quran! There's nothing left to send. May it be accepted 🤍",
    },
    # --- Create-khatm wizard keyboards (i18n; BACKLOG #1) ---
    "ck.mode.commitment": {"fa": "🔒 تعهدی (سهم مشخص برای هرکس)", "ar": "🔒 التزامي (حصة محددة لكل شخص)", "en": "🔒 Commitment (a set share each)"},
    "ck.mode.open": {"fa": "🌿 آزاد (هرکس با میل خودش)", "ar": "🌿 حر (كلٌّ حسب رغبته)", "en": "🌿 Open (each at their own pace)"},
    "ck.tpl.quran": {"fa": "📖 ختم قرآن", "ar": "📖 ختم القرآن", "en": "📖 Quran khatm"},
    "ck.tpl.salawat": {"fa": "📿 ختم صلوات", "ar": "📿 ختم الصلوات", "en": "📿 Salawat khatm"},
    "ck.tpl.dua": {"fa": "🤲 ختم دعا و زیارت", "ar": "🤲 ختم الدعاء والزيارة", "en": "🤲 Dua & Ziyarat khatm"},
    "ck.tpl.laan": {"fa": "🗡 ختم لعن", "ar": "🗡 ختم اللعن", "en": "🗡 La'n khatm"},
    "ck.cat.custom": {"fa": "➕ دعا یا زیارت دیگر", "ar": "➕ دعاء أو زيارة أخرى", "en": "➕ Another dua or ziyarat"},
    "ck.skip_niyyat": {"fa": "رد کردن ⏭", "ar": "تخطٍّ ⏭", "en": "Skip ⏭"},
    "ck.content_mode.auto": {"fa": "⚙️ خودکار (هرچه موجود بود)", "ar": "⚙️ تلقائي (ما هو متوفر)", "en": "⚙️ Auto (whatever exists)"},
    "ck.content_mode.photo": {"fa": "🖼 فقط تصویر صفحات", "ar": "🖼 صور الصفحات فقط", "en": "🖼 Page images only"},
    "ck.content_mode.text": {"fa": "📝 فقط متن صفحات", "ar": "📝 نص الصفحات فقط", "en": "📝 Page text only"},
    "ck.tone.friendly": {"fa": "🌱 صمیمی", "ar": "🌱 ودّي", "en": "🌱 Friendly"},
    "ck.tone.formal": {"fa": "📜 رسمی", "ar": "📜 رسمي", "en": "📜 Formal"},
    "ck.tone.devotional": {"fa": "🤍 معنوی", "ar": "🤍 روحاني", "en": "🤍 Devotional"},
    "ck.tone.short": {"fa": "⚡ کوتاه", "ar": "⚡ قصير", "en": "⚡ Short"},
    "ck.display.full": {"fa": "👤 نام کامل", "ar": "👤 الاسم الكامل", "en": "👤 Full name"},
    "ck.display.first": {"fa": "🙂 فقط نام کوچک", "ar": "🙂 الاسم الأول فقط", "en": "🙂 First name only"},
    "ck.display.pseudonym": {"fa": "🪪 نام مستعار", "ar": "🪪 اسم مستعار", "en": "🪪 Pseudonym"},
    "ck.display.institution": {"fa": "🏢 نام مؤسسه/سازمان", "ar": "🏢 اسم المؤسسة/المنظمة", "en": "🏢 Institution / organization"},
    "ck.display.anonymous": {"fa": "🤲 ناشناس / نیکوکار", "ar": "🤲 مجهول / محسِن", "en": "🤲 Anonymous / benefactor"},
    "ck.start.now": {"fa": "▶️ همین حالا", "ar": "▶️ الآن", "en": "▶️ Right now"},
    "ck.start.future": {"fa": "🗓 شروع در تاریخ آینده", "ar": "🗓 البدء في تاريخ لاحق", "en": "🗓 Start on a future date"},
    "ck.capacity.limited": {"fa": "🔢 ظرفیت محدود", "ar": "🔢 سعة محدودة", "en": "🔢 Limited capacity"},
    "ck.capacity.unlimited": {"fa": "♾ نامحدود", "ar": "♾ غير محدود", "en": "♾ Unlimited"},
    "ck.visibility.public": {"fa": "🌍 عمومی (در فهرست ختم‌ها نمایش داده شود)", "ar": "🌍 عام (يظهر في قائمة الختمات)", "en": "🌍 Public (listed)"},
    "ck.visibility.unlisted": {"fa": "🔗 با لینک، برای همه باز", "ar": "🔗 بالرابط، مفتوح للجميع", "en": "🔗 Link-only, open to all"},
    "ck.visibility.private": {"fa": "🔒 عضویت نیاز به تایید من داره", "ar": "🔒 الانضمام يحتاج موافقتي", "en": "🔒 Joining needs my approval"},
    "ck.ads.on": {"fa": "✅ بله، تبلیغات فعال باشد", "ar": "✅ نعم، فعّل الإعلانات", "en": "✅ Yes, enable ads"},
    "ck.ads.off": {"fa": "🚫 خیر، بدون تبلیغات", "ar": "🚫 لا، بدون إعلانات", "en": "🚫 No ads"},
    "ck.confirm": {"fa": "✅ تایید و شروع ختم", "ar": "✅ تأكيد وبدء الختمة", "en": "✅ Confirm & start"},
    "ck.coupon": {"fa": "🎟 کد تخفیف دارم", "ar": "🎟 لديّ رمز خصم", "en": "🎟 I have a coupon"},
    "ck.coupon_back": {"fa": "🔙 ادامه بدون کد", "ar": "🔙 المتابعة بدون رمز", "en": "🔙 Continue without code"},
    "ck.back": {"fa": "⬅️ مرحلهٔ قبل", "ar": "⬅️ الخطوة السابقة", "en": "⬅️ Previous step"},
    "ck.cancel": {"fa": "❌ انصراف", "ar": "❌ إلغاء", "en": "❌ Cancel"},
    # --- Creator khatm-management keyboards (cs:* tree, i18n) ---
    "cs.members": {"fa": "👥 لیست اعضا", "ar": "👥 قائمة الأعضاء", "en": "👥 Members"},
    "cs.export": {"fa": "📄 خروجی CSV", "ar": "📄 تصدير CSV", "en": "📄 CSV export"},
    "cs.qr": {"fa": "🔳 QR دعوت", "ar": "🔳 QR الدعوة", "en": "🔳 Invite QR"},
    "cs.stats": {"fa": "📈 آمار ختم", "ar": "📈 إحصاءات الختمة", "en": "📈 Khatm stats"},
    "cs.settings": {"fa": "⚙️ تنظیمات ختم", "ar": "⚙️ إعدادات الختمة", "en": "⚙️ Khatm settings"},
    "cs.cancel_khatm": {"fa": "🗑 لغو ختم", "ar": "🗑 إلغاء الختمة", "en": "🗑 Cancel khatm"},
    "cs.title": {"fa": "✏️ عنوان", "ar": "✏️ العنوان", "en": "✏️ Title"},
    "cs.welcome": {"fa": "💬 پیام خوش‌آمد", "ar": "💬 رسالة الترحيب", "en": "💬 Welcome message"},
    "cs.target": {"fa": "🔢 افزایش هدف کل", "ar": "🔢 زيادة الهدف", "en": "🔢 Increase total goal"},
    "cs.deadline": {"fa": "⏰ ساعت پایان مهلت", "ar": "⏰ ساعة انتهاء المهلة", "en": "⏰ Deadline hour"},
    "my_khatms.creator.ask_new_target": {"fa": "هدف کل جدید را بنویسید. برای حفظ سابقهٔ اعضا، عدد جدید باید برابر یا بیشتر از هدف فعلی باشد.", "ar": "اكتب الهدف الكلي الجديد؛ يجب ألا يقل عن الهدف الحالي.", "en": "Type the new total goal. It cannot be lower than the current goal."},
    "my_khatms.creator.ask_new_deadline": {"fa": "ساعت جدید پایان مهلت روزانه را با عددی بین ۰ تا ۲۳ بنویسید.", "ar": "اكتب ساعة انتهاء المهلة بين 0 و23.", "en": "Type the new daily deadline hour from 0 to 23."},
    "my_khatms.creator.target_saved": {"fa": "✅ هدف کل به {value} افزایش یافت.", "ar": "✅ تم تحديث الهدف إلى {value}.", "en": "✅ Total goal updated to {value}."},
    "my_khatms.creator.deadline_saved": {"fa": "✅ پایان مهلت روزانه ساعت {value} تنظیم شد.", "ar": "✅ تم ضبط الموعد عند الساعة {value}.", "en": "✅ Daily deadline set to {value}:00."},
    "cs.end_date": {"fa": "🗓 پایان تاریخی", "ar": "🗓 تاريخ الانتهاء", "en": "🗓 End date"},
    "cs.end_clear": {"fa": "🧹 حذف پایان", "ar": "🧹 حذف تاريخ الانتهاء", "en": "🧹 Clear end date"},
    "cs.schedule": {"fa": "⏰ زمان‌بندی مشارکت", "ar": "⏰ جدولة المشاركة", "en": "⏰ Participation schedule"},
    "cs.content_fmt": {"fa": "📖 فرمت محتوا: {mode}", "ar": "📖 صيغة المحتوى: {mode}", "en": "📖 Content format: {mode}"},
    "cs.content_mode.auto": {"fa": "خودکار", "ar": "تلقائي", "en": "Auto"},
    "cs.content_mode.photo": {"fa": "فقط تصویر", "ar": "صور فقط", "en": "Images only"},
    "cs.content_mode.text": {"fa": "فقط متن", "ar": "نص فقط", "en": "Text only"},
    "cs.pause_toggle": {"fa": "توقف موقت تعهد", "ar": "إيقاف مؤقت للالتزام", "en": "Pause commitment"},
    "cs.snooze_toggle": {"fa": "تعویق یادآوری", "ar": "تأجيل التذكير", "en": "Snooze reminders"},
    "cs.back_my_khatms": {"fa": "🔙 ختم‌های من", "ar": "🔙 ختماتي", "en": "🔙 My khatms"},
    "cs.edit_cancel": {"fa": "🔙 انصراف و بازگشت", "ar": "🔙 إلغاء ورجوع", "en": "🔙 Cancel & back"},
    "cs.mode_auto": {"fa": "⚙️ خودکار (پیشنهادی)", "ar": "⚙️ تلقائي (موصى به)", "en": "⚙️ Auto (recommended)"},
    "cs.mode_photo": {"fa": "🖼 فقط تصویر", "ar": "🖼 صور فقط", "en": "🖼 Images only"},
    "cs.mode_text": {"fa": "📝 فقط متن", "ar": "📝 نص فقط", "en": "📝 Text only"},
    "cs.back": {"fa": "🔙 بازگشت", "ar": "🔙 رجوع", "en": "🔙 Back"},
    "cs.sched.off": {"fa": "🚫 بدون زمان‌بندی", "ar": "🚫 بدون جدولة", "en": "🚫 No schedule"},
    "cs.sched.daily": {"fa": "📅 هر روز", "ar": "📅 كل يوم", "en": "📅 Every day"},
    "cs.sched.workdays": {"fa": "💼 روزهای کاری", "ar": "💼 أيام العمل", "en": "💼 Weekdays"},
    "cs.sched.weekend": {"fa": "🌿 آخرهفته", "ar": "🌿 عطلة الأسبوع", "en": "🌿 Weekend"},
    "cs.sched.every3": {"fa": "🔁 هر ۳ روز", "ar": "🔁 كل ۳ أيام", "en": "🔁 Every 3 days"},
    "cs.sched.date": {"fa": "🗓 یک تاریخ مشخص", "ar": "🗓 تاريخ محدد", "en": "🗓 A specific date"},
    "cs.cancel_confirm": {"fa": "✅ لغو و بازپرداخت", "ar": "✅ الإلغاء والاسترداد", "en": "✅ Cancel & refund"},
    # --- Member-facing pause / leave keyboards (i18n) ---
    "pause.duration.3": {"fa": "۳ روز", "ar": "۳ أيام", "en": "3 days"},
    "pause.duration.7": {"fa": "۷ روز", "ar": "۷ أيام", "en": "7 days"},
    "pause.duration.14": {"fa": "۱۴ روز", "ar": "۱۴ يومًا", "en": "14 days"},
    "pause.duration.custom": {"fa": "🗓 تا تاریخ مشخص", "ar": "🗓 حتى تاريخ محدد", "en": "🗓 Until a set date"},
    "leave.reason.busy": {"fa": "فعلاً وقت ندارم", "ar": "لا وقت لديّ حالياً", "en": "No time right now"},
    "leave.reason.mistake": {"fa": "اشتباهی عضو شدم", "ar": "انضممت بالخطأ", "en": "Joined by mistake"},
    "leave.reason.notifications": {"fa": "مشکل در دریافت پیام", "ar": "مشكلة في استلام الرسائل", "en": "Trouble receiving messages"},
    "leave.reason.other": {"fa": "سایر", "ar": "أخرى", "en": "Other"},
    "member.welcome": {
        "fa": "سلام، خوش اومدید 🌿\n\nاینجا می‌تونید در ختم‌ها شرکت کنید و سهم روزانه‌تون رو بگیرید.\nبا لینک دعوت وارد یک ختم بشید، یا از دکمه‌های پایین استفاده کنید.",
        "ar": "مرحباً بك 🌿\n\nمن هنا يمكنك المشاركة في الختمات واستلام حصتك اليومية.\nادخل ختمة عبر رابط الدعوة، أو استخدم الأزرار في الأسفل.",
        "en": "Welcome 🌿\n\nHere you can join khatms and receive your daily portion.\nJoin a khatm through an invite link, or use the buttons below.",
    },
    "my_khatms.button.leave": {
        "fa": "خروج از ختم", "ar": "الخروج من الختمة", "en": "Leave khatm",
    },
    "my_khatms.button.reminder_hour": {
        "fa": "⏰ ساعت یادآوری", "ar": "⏰ وقت التذكير", "en": "⏰ Reminder time",
    },
    "my_khatms.pick_reminder_hour": {
        "fa": "چه ساعتی یادآوری این ختم برایتان فرستاده شود؟\nیکی از دکمه‌ها را بزنید، یا ساعت دقیق را بنویسید (مثلاً 14:40):",
        "ar": "في أي وقت تريد تذكير هذه الختمة؟\nاضغط أحد الأزرار أو اكتب الوقت بدقة (مثلاً 14:40):",
        "en": "What time should this khatm's reminder be sent?\nTap a button, or type an exact time (e.g. 14:40):",
    },
    "join.error.wrong_bot": {
        "fa": "این ختم مربوط به بات دیگری است.",
        "ar": "هذه الختمة تخص بوتاً آخر.",
        "en": "This khatm belongs to a different bot.",
    },
    "join.error.platform_restricted": {
        "fa": "این ختم فقط برای کاربران پیام‌رسان {platform} ایجاد شده است.",
        "ar": "هذه الختمة مخصصة فقط لمستخدمي {platform}.",
        "en": "This khatm is only for {platform} users.",
    },
    "join.menu_hint": {
        "fa": "از منوی پایین می‌تونید سهم امروز و ختم‌هاتون رو ببینید 🌿",
        "ar": "من القائمة في الأسفل يمكنك رؤية حصة اليوم وختماتك 🌿",
        "en": "Use the menu below to see today's portion and your khatms 🌿",
    },
    "join.button.join": {
        "fa": "✅ شرکت در این ختم", "ar": "✅ المشاركة في هذه الختمة", "en": "✅ Join this khatm",
    },
    "join.button.cancel": {
        "fa": "❌ انصراف", "ar": "❌ إلغاء", "en": "❌ Cancel",
    },
    "join.button.accept_commitment": {
        "fa": "✅ تعهد را می‌پذیرم", "ar": "✅ أقبل الالتزام", "en": "✅ I accept the commitment",
    },
    "join.button.accept_open_rules": {
        "fa": "✅ متوجه شدم؛ ادامه می‌دهم", "ar": "✅ فهمت؛ أتابع", "en": "✅ I understand; continue",
    },
    "join.consent.fixed_daily_rule": {
        "fa": (
            "⏳ <b>توجه: این ختم تعهدی است.</b>\n"
            "سازنده این ختم، مقدار {amount} {unit} را به صورت ثابت و روزانه برای هر عضو در نظر گرفته است.\n"
            "با ورود به این ختم، متعهد می‌شوید که این مقدار را به صورت منظم ادا نمایید.\n\n"
            "اگر مایلید در این ختم شرکت کنید، دکمه تأیید را بزنید."
        ),
        "ar": (
            "⏳ <b>انتباه: هذا ختم إلزامي.</b>\n"
            "حدد المنشئ كمية يومية ثابتة وهي {amount} {unit} لكل عضو.\n"
            "بانضمامك، أنت تلتزم بأداء هذا المقدار بانتظام.\n\n"
            "إذا كنت ترغب في المشاركة، اضغط على زر التأكيد."
        ),
        "en": (
            "⏳ <b>Note: This is a commitment khatm.</b>\n"
            "The creator has set a fixed daily amount of {amount} {unit} for each member.\n"
            "By joining, you commit to completing this amount regularly.\n\n"
            "If you wish to participate, please tap the confirm button."
        ),
    },
    "join.consent.commitment_rule": {
        "fa": (
            "⚠️ <b>توجه: این ختم تعهدی است.</b>\n"
            "با تأیید، سهمی که انتخاب می‌کنید لازم است حتماً خوانده شود، "
            "چون پیشرفت ختم و دور بعدی منتظر سهم شماست 🌱\n\n"
            "اگر مطمئن هستید که می‌توانید انجامش دهید، تعهد را تأیید کنید."
        ),
        "ar": "⚠️ <b>تنبيه: هذه ختمة التزام.</b> الحصة أو البرنامج الذي تختاره ضروري لإكمال الختمة مع بقية المشاركين.",
        "en": "⚠️ <b>Note: this is a committed khatm.</b> The portion or schedule you choose is essential to complete the khatm with others.",
    },
    "join.consent.open_rule": {
        "fa": (
            "🌱 <b>توجه: این ختم آزاد است.</b>\n"
            "سهمی که انتخاب می‌کنید التزام قطعی ایجاد نمی‌کند؛ بااین‌حال همراهی شما به پیشرفت و تکمیل ختم جمعی کمک شایانی خواهد کرد 🌱\n\n"
            "اگر مایل به همراهی هستید، ادامه را تأیید کنید."
        ),
        "ar": "🌱 <b>تنبيه: هذه ختمة مفتوحة.</b> شارك بقدر ما تستطيع لمساعدة الختمة الجماعية.",
        "en": "🌱 <b>Note: this is an open khatm.</b> Contribute as much as you wish to support the collective khatm.",
    },
    "join.ask_delivery_hour": {
        "fa": "یک سؤال کوتاه دیگه 🌱\n\nچه موقعی از روز دوست دارید سهم هر روزتون خودکار براتون فرستاده بشه؟ یکی از دکمه‌های زیر رو بزنید، یا اگه ساعت دقیق‌تری مدنظرتونه، فقط عددش رو بنویسید (بین 0 تا 23):",
        "ar": "سؤال قصير آخر 🌱\n\nفي أي وقت من اليوم تحب أن تصلك حصتك اليومية تلقائياً؟ اضغط أحد الأزرار أدناه، أو إذا أردت ساعة دقيقة أرسل رقمها (بين 0 و23):",
        "en": "One more quick question 🌱\n\nWhat time of day would you like your daily portion sent automatically? Tap one of the buttons below, or type an exact hour (0 to 23) if you prefer:",
    },
    "delivery_hour.early_morning": {"fa": "🌅 صبح زود", "ar": "🌅 الفجر", "en": "🌅 Early morning"},
    "delivery_hour.morning": {"fa": "☀️ صبح", "ar": "☀️ الصباح", "en": "☀️ Morning"},
    "delivery_hour.noon": {"fa": "🌞 ظهر", "ar": "🌞 الظهر", "en": "🌞 Noon"},
    "delivery_hour.afternoon": {"fa": "🌤 بعدازظهر", "ar": "🌤 بعد الظهر", "en": "🌤 Afternoon"},
    "delivery_hour.evening": {"fa": "🌇 غروب", "ar": "🌇 المساء", "en": "🌇 Evening"},
    "delivery_hour.night": {"fa": "🌙 شب", "ar": "🌙 الليل", "en": "🌙 Night"},
    "join.delivery_hour_invalid": {
        "fa": "یک عدد بین 0 تا 23 بفرستید، مثلاً 9.", "ar": "أرسل رقماً بين 0 و23، مثلاً 9.",
        "en": "Please send a number between 0 and 23, like 9.",
    },
    "join.delivery_hour_saved": {
        "fa": "تنظیم شد ✅ هر روز ساعت {hour} به وقت خودتون، سهم روزانه‌تون خودکار براتون فرستاده می‌شه.",
        "ar": "تم الإعداد ✅ كل يوم الساعة {hour} بتوقيتك، سترسل لك حصتك اليومية تلقائياً.",
        "en": "All set ✅ Every day at {hour} your time, your daily portion will be sent to you automatically.",
    },
    "portions.open_quran.pages_sent": {
        "fa": "📖 صفحات {start} تا {end} براتون فرستاده شد.", "ar": "📖 أُرسلت لك الصفحات من {start} إلى {end}.",
        "en": "📖 Pages {start} to {end} were sent to you.",
    },
    "portions.open_surplus_split": {
        "fa": "از این تعداد، {counted} {unit} برای تکمیل ختم و {surplus} {unit} به‌عنوان مشارکت مازاد شما ثبت شد 🌱",
        "ar": "من هذا العدد، تم تسجيل {counted} {unit} لإكمال الختمة و{surplus} {unit} كمشاركة إضافية منك 🌱",
        "en": "Of that amount, {counted} {unit} was logged toward completing the khatm and {surplus} {unit} as your surplus contribution 🌱",
    },
    "portions.overall_progress": {
        "fa": "پیشرفت کلی ختم: {done} از {target}", "ar": "التقدم الكلي للختمة: {done} من {target}",
        "en": "Overall khatm progress: {done} of {target}",
    },
    "portions.today_vs_yesterday": {
        "fa": "📈 مجموع {unit} این ختم امروز (تا این لحظه): {today}\nدیروز (کل روز): {yesterday}",
        "ar": "📈 مجموع {unit} هذه الختمة اليوم (حتى الآن): {today}\nأمس (اليوم الكامل): {yesterday}",
        "en": "📈 This khatm's total {unit} today (so far): {today}\nYesterday (full day): {yesterday}",
    },
    "portions.goal_reached": {
        "fa": "\n🎉 هدف این ختم تکمیل شد! خدا قبول کنه 🤍", "ar": "\n🎉 اكتمل هدف هذه الختمة! تقبّل الله 🤍",
        "en": "\n🎉 This khatm's goal has been reached! May it be accepted 🤍",
    },
    "portions.pause_not_allowed": {
        "fa": "توقف موقت برای این ختم فعال نیست.", "ar": "الإيقاف المؤقت غير مفعّل لهذه الختمة.",
        "en": "Pausing isn't enabled for this khatm.",
    },
    "portions.ask_pause_days": {
        "fa": "تعهدتون رو چند روز متوقف کنیم؟ در این مدت سهمتون به بقیه می‌رسه و غیبت هم ثبت نمی‌شه:",
        "ar": "كم يوماً نوقف التزامك؟ خلال هذه المدة تنتقل حصتك للآخرين ولن يُسجَّل غياب:",
        "en": "For how many days should we pause your commitment? During this time your portion goes to others and no miss is logged:",
    },
    "portions.ask_custom_pause_until": {
        "fa": "تاریخ پایان توقف را به وقت تهران بفرستید: YYYY-MM-DD HH:MM",
        "ar": "أرسل تاريخ انتهاء الإيقاف بتوقيت طهران: YYYY-MM-DD HH:MM",
        "en": "Send the pause end date in Tehran time: YYYY-MM-DD HH:MM",
    },
    "portions.pause_date_format_invalid": {
        "fa": "قالب تاریخ درست نیست. نمونه: 2026-10-01 23:00", "ar": "صيغة التاريخ غير صحيحة. مثال: 2026-10-01 23:00",
        "en": "Invalid date format. Example: 2026-10-01 23:00",
    },
    "portions.pause_must_be_future": {
        "fa": "تاریخ پایان توقف باید در آینده باشد.", "ar": "يجب أن يكون تاريخ انتهاء الإيقاف في المستقبل.",
        "en": "The pause end date must be in the future.",
    },
    "portions.khatm_inactive_or_not_yours": {
        "fa": "این ختم فعال نیست یا شما عضو آن نیستید.", "ar": "هذه الختمة غير نشطة أو لست عضواً فيها.",
        "en": "This khatm isn't active, or you're not a member of it.",
    },
    "portions.pause_custom_saved": {
        "fa": "تعهد شما تا تاریخ انتخاب‌شده متوقف شد 🤍", "ar": "تم إيقاف التزامك حتى التاريخ المحدد 🤍",
        "en": "Your commitment was paused until the chosen date 🤍",
    },
    "portions.pause_days_saved": {
        "fa": "تعهدتون برای {days} روز متوقف شد 🤍 هر وقت خواستید از «🕋 ختم‌های من» «ادامه تعهد» رو بزنید.",
        "ar": "تم إيقاف التزامك لمدة {days} يوماً 🤍 متى أردت اضغط «استئناف الالتزام» من «ختماتي».",
        "en": "Your commitment was paused for {days} days 🤍 Whenever you'd like, tap “Resume commitment” from “My khatms”.",
    },
    "portions.resumed": {
        "fa": "تعهدتون دوباره فعال شد ✅", "ar": "تم استئناف التزامك ✅", "en": "Your commitment is active again ✅",
    },
    "portions.invite_friends_line": {
        "fa": "\n\nبا ارسال این لینک برای دوستانتون، اون‌ها رو هم به مشارکت در همین ثواب دعوت کنید:\n{invite_url}",
        "ar": "\n\nبإرسال هذا الرابط لأصدقائك، ادعهم للمشاركة في هذا الثواب أيضاً:\n{invite_url}",
        "en": "\n\nBy sending this link to your friends, invite them to share in this same reward too:\n{invite_url}",
    },

    # --- report.py (2026-09-20) ---
    "report.no_portion_today": {
        "fa": "برای امروز سهم فعالی ندارید 🌱", "ar": "ليس لديك حصة نشطة لليوم 🌱", "en": "You don't have an active portion for today 🌱",
    },
    "report.today_count": {
        "fa": "📅 سهم‌های امروز شما: {count}", "ar": "📅 حصص اليوم لديك: {count}", "en": "📅 Your portions for today: {count}",
    },
    "report.today_page_label": {
        "fa": "«{title}» — صفحات {start} تا {end}", "ar": "«{title}» — الصفحات من {start} إلى {end}",
        "en": "“{title}” — pages {start} to {end}",
    },
    "report.today_quantity_label": {
        "fa": "«{title}» — {quantity} بار", "ar": "«{title}» — {quantity} مرة", "en": "“{title}” — {quantity} time(s)",
    },
    "report.header": {
        "fa": "📊 گزارش همراهی شما", "ar": "📊 تقرير مشاركتك", "en": "📊 Your participation report",
    },
    "report.active_khatms": {
        "fa": "ختم‌های فعال: {count}", "ar": "الختمات النشطة: {count}", "en": "Active khatms: {count}",
    },
    "report.completed_khatms": {
        "fa": "ختم‌های به پایان‌رسیده: {count}", "ar": "الختمات المنتهية: {count}", "en": "Completed khatms: {count}",
    },
    "report.completed_portions_month": {
        "fa": "سهم‌های کامل‌شده در این ماه: {count}", "ar": "الحصص المكتملة هذا الشهر: {count}",
        "en": "Portions completed this month: {count}",
    },
    "report.completed_portions_total": {
        "fa": "مجموع سهم‌های کامل‌شده: {count}", "ar": "إجمالي الحصص المكتملة: {count}",
        "en": "Total portions completed: {count}",
    },
    "report.contributions_month": {
        "fa": "مشارکت ثبت‌شده در این ماه: {amount}", "ar": "المشاركة المسجَّلة هذا الشهر: {amount}",
        "en": "Contributions logged this month: {amount}",
    },
    "report.closing_line": {
        "fa": "\nهمراهی شما ارزشمند است؛ خدا قبول کند 🤍", "ar": "\nمشاركتك قيّمة؛ تقبّل الله 🤍",
        "en": "\nYour participation is valuable; may it be accepted 🤍",
    },

    # --- leave.py (2026-09-20) ---
    "leave.ask_reason": {
        "fa": "قبل از خروج، اگه بخواید بگید چرا (اختیاری نیست ولی سریعه):",
        "ar": "قبل الخروج، إذا أردت أخبرنا لماذا (ليس اختيارياً لكنه سريع):",
        "en": "Before leaving, if you'd like, tell us why (not optional, but quick):",
    },
    "leave.membership_not_found": {
        "fa": "این عضویت پیدا نشد.", "ar": "لم يتم العثور على هذه العضوية.", "en": "This membership wasn't found.",
    },
    "leave.default_member_name": {"fa": "یکی از اعضا", "ar": "أحد الأعضاء", "en": "one of the members"},
    "leave.requester_waiting_for_creator": {
        "fa": "درخواست خروجتون برای سازنده ختم ارسال شد؛ چون عضو تعهدی هستید، اول باید تایید کنه تا "
        "ختم بقیه به‌هم نریزه. منتظر بمونید 🌱",
        "ar": "أُرسل طلب خروجك إلى منشئ الختمة؛ بما أنك عضو ملتزم، يجب أن يوافق أولاً حتى لا تتعطل "
        "الختمة على الآخرين. انتظر قليلاً 🌱",
        "en": "Your leave request was sent to the khatm's creator; since you're a committed member, they need to "
        "approve first so it doesn't disrupt things for others. Please wait 🌱",
    },
    "leave.creator_notify": {
        "fa": "{name} می‌خواد از بخش تعهدی «{title}» خارج بشه.",
        "ar": "{name} يريد الخروج من القسم الملتزم لـ«{title}».",
        "en": "{name} wants to leave the commitment section of “{title}”.",
    },
    "leave.approve_button": {"fa": "✅ تایید خروج", "ar": "✅ الموافقة على الخروج", "en": "✅ Approve leaving"},
    "leave.reject_button": {"fa": "❌ رد", "ar": "❌ رفض", "en": "❌ Reject"},
    "leave.approved_creator_side": {
        "fa": "خروج تایید شد؛ عضو از بخش تعهدی این ختم خارج شد و به او اطلاع داده شد.",
        "ar": "تمت الموافقة على الخروج؛ خرج العضو من القسم الملتزم لهذه الختمة وتم إبلاغه.",
        "en": "Leaving was approved; the member left this khatm's commitment section and was notified.",
    },
    "leave.approved_requester_side": {
        "fa": "درخواست خروجتون تایید شد و از ختم خارج شدید.", "ar": "تمت الموافقة على طلب خروجك وخرجت من الختمة.",
        "en": "Your leave request was approved and you left the khatm.",
    },
    "leave.rejected_creator_side": {
        "fa": "درخواست رد شد؛ عضو همچنان تعهدیه.", "ar": "تم رفض الطلب؛ العضو ما زال ملتزماً.",
        "en": "The request was rejected; the member is still committed.",
    },
    "leave.rejected_requester_side": {
        "fa": "سازنده ختم فعلاً درخواست خروجتون رو تایید نکرد؛ همچنان عضو تعهدی این ختم هستید 🤍",
        "ar": "لم يوافق منشئ الختمة على طلب خروجك حالياً؛ ما زلت عضواً ملتزماً في هذه الختمة 🤍",
        "en": "The khatm's creator hasn't approved your leave request for now; you're still a committed member of this khatm 🤍",
    },
    "leave.left_khatm": {
        "fa": "از ختم «{title}» خارج شدید.", "ar": "خرجت من ختمة «{title}».", "en": "You left the khatm “{title}”.",
    },
    "leave.promoted_notice": {
        "fa": "🎉 یک جای تعهدی در «{title}» خالی شد و شما جایگزین شدید!",
        "ar": "🎉 توفر مكان ملتزم في «{title}» وأصبحت البديل!",
        "en": "🎉 A committed spot opened up in “{title}” and you've been promoted into it!",
    },
    "leave.promoted_portion_line": {
        "fa": "\n\nسهم شما: صفحات {start} تا {end}", "ar": "\n\nحصتك: الصفحات من {start} إلى {end}",
        "en": "\n\nYour portion: pages {start} to {end}",
    },

    # --- join.success message: shared by start.py (direct join) and
    # join_requests.py (private-khatm approval) (2026-09-20) ---
    "join.welcome_line": {
        "fa": "خوش آمدید {name} 🌱\nبه «{title}» پیوستید.",
        "ar": "أهلاً بك {name} 🌱\nانضممت إلى «{title}».",
        "en": "Welcome {name} 🌱\nYou joined “{title}”.",
    },
    "join.creator_line": {
        "fa": "\nاین ختم از طرف {name} است.", "ar": "\nهذه الختمة مقدمة من {name}.", "en": "\nThis khatm is from {name}.",
    },
    "join.trust.invited": {
        "fa": "🌱 دعوت به ختم «{title}»",
        "ar": "🌱 دعوة إلى ختمة «{title}»",
        "en": "🌱 Invitation to the khatm “{title}”",
    },
    "join.trust.from": {
        "fa": "\nسازندهٔ ختم: {creator}",
        "ar": "\nهذه الختمة مقدمة من {creator}.",
        "en": "\nThis khatm is from {creator}.",
    },
    "join.trust.niyyat": {
        "fa": "\nبه نیت: {niyyat}", "ar": "\nبنية: {niyyat}", "en": "\nIntention: {niyyat}",
    },
    "join.niyyat_line": {
        "fa": "\nبه نیت: {niyyat}", "ar": "\nبنية: {niyyat}", "en": "\nIntention: {niyyat}",
    },
    "join.welcome_text_line": {
        "fa": "\n\n{text}", "ar": "\n\n{text}", "en": "\n\n{text}",
    },
    "join.trust_privacy_caption": {
        "fa": "🔒 همه با لینک اختصاصی شما وارد می‌شوند و با اعضای ختم‌های دیگر قاطی نمی‌شوند. مخاطبان این ختم برای خودتان هستند و دیگران به فهرستشان دسترسی ندارند. همچنین می‌توانید در صورت نیاز به آن‌ها پیام خصوصی ارسال کنید.",
        "ar": "🔒 يدخل الجميع عبر رابطك الخاص ولا يختلطون بأعضاء الختمات الأخرى. جمهور هذه الختمة لك وحدك ولا يصل إليه غيرك. ويمكنك أيضاً مراسلتهم بشكل خاص عند الحاجة.",
        "en": "🔒 Everyone joins via your own link and never mixes with other khatms' members. This khatm's audience is yours alone, and you can message them privately if needed.",
    },
    "join.waitlisted_line": {
        "fa": "\n\nظرفیت بخش تعهدی این ختم پره — فعلاً تو لیست انتظارید، ولی می‌تونید همین حالا "
        "بدون تعهد و آزادانه همراه ختم مشارکت کنید. به‌محض خالی شدن جا، بهتون اطلاع می‌دیم.",
        "ar": "\n\nامتلأت سعة القسم الملتزم لهذه الختمة — أنت حالياً في قائمة الانتظار، لكن يمكنك المشاركة "
        "بحرية الآن دون التزام. بمجرد توفر مكان سنبلغك.",
        "en": "\n\nThis khatm's commitment section is full — you're on the waiting list for now, but you "
        "can freely contribute without a pledge right away. We'll let you know as soon as a spot opens up.",
    },
    "join.first_page_portion_line": {
        "fa": "\n\nسهم اول شما: صفحات {start} تا {end}", "ar": "\n\nحصتك الأولى: الصفحات من {start} إلى {end}",
        "en": "\n\nYour first portion: pages {start} to {end}",
    },
    "join.first_quantity_portion_line": {
        "fa": "\n\nسهم شما: {quantity} بار", "ar": "\n\nحصتك: {quantity} مرة", "en": "\n\nYour portion: {quantity} time(s)",
    },
    "join.no_open_portion_line": {
        "fa": "\n\nدر حال حاضر سهم باز دیگری برای شما باقی نمونده — به‌محض آزاد شدن یک سهم بهتون اطلاع می‌دیم.",
        "ar": "\n\nلا توجد حالياً حصة مفتوحة أخرى لك — بمجرد توفر حصة سنبلغك.",
        "en": "\n\nThere's no other open portion left for you right now — we'll let you know as soon as one frees up.",
    },
    "join.creator_display.anonymous": {"fa": "یک نیکوکار", "ar": "أحد المحسنين", "en": "a benefactor"},
    "join.default_display_name": {"fa": "کاربر", "ar": "مستخدم", "en": "user"},

    # --- join_requests.py (2026-09-20) ---
    "join_requests.account_not_found": {
        "fa": "حساب شما پیدا نشد.", "ar": "لم يتم العثور على حسابك.", "en": "Your account wasn't found.",
    },
    "join_requests.only_creator_can_approve": {
        "fa": "فقط سازندهٔ همین ختم می‌تواند درخواست را تأیید کند.",
        "ar": "فقط منشئ هذه الختمة يمكنه الموافقة على الطلب.",
        "en": "Only this khatm's creator can approve the request.",
    },
    "join_requests.only_creator_can_reject": {
        "fa": "فقط سازندهٔ همین ختم می‌تواند درخواست را رد کند.",
        "ar": "فقط منشئ هذه الختمة يمكنه رفض الطلب.",
        "en": "Only this khatm's creator can reject the request.",
    },
    "join_requests.already_member": {
        "fa": "این فرد از قبل عضو این ختمه.", "ar": "هذا الشخص عضو بالفعل في هذه الختمة.",
        "en": "This person is already a member of this khatm.",
    },
    "join_requests.khatm_not_active": {
        "fa": "این ختم دیگر فعال نیست.", "ar": "هذه الختمة لم تعد نشطة.", "en": "This khatm is no longer active.",
    },
    "join_requests.approved_creator_side": {
        "fa": "عضویت تایید شد ✅ به این فرد اطلاع داده شد و حالا عضو ختم شماست.",
        "ar": "تمت الموافقة على العضوية ✅ تم إبلاغ الشخص وهو الآن عضو في ختمتك.",
        "en": "Membership approved ✅ This person was notified and is now a member of your khatm.",
    },
    "join_requests.rejected_creator_side": {
        "fa": "درخواست رد شد؛ به درخواست‌دهنده اطلاع داده شد.",
        "ar": "تم رفض الطلب؛ تم إبلاغ مقدم الطلب.",
        "en": "The request was rejected; the requester was notified.",
    },
    "join_requests.rejected_requester_side": {
        "fa": "درخواست عضویتتون در «{title}» تایید نشد.", "ar": "لم تتم الموافقة على طلب عضويتك في «{title}».",
        "en": "Your membership request for “{title}” wasn't approved.",
    },
    "join_requests.this_khatm_fallback": {"fa": "این ختم", "ar": "هذه الختمة", "en": "this khatm"},

    # --- wallet.py (2026-09-20) ---
    "wallet.plan_label.FREE": {"fa": "رایگان", "ar": "مجانية", "en": "Free"},
    "wallet.plan_label.BASIC": {"fa": "پایه", "ar": "أساسية", "en": "Basic"},
    "wallet.plan_label.PRO": {"fa": "حرفه‌ای", "ar": "احترافية", "en": "Pro"},
    "wallet.topup_button": {
        "fa": "{amount} هزار تومان", "ar": "{amount} ألف تومان", "en": "{amount}k toman",
    },
    "wallet.topup_custom_button": {
        "fa": "💰 مبلغ دلخواه", "ar": "💰 مبلغ مخصص", "en": "💰 Custom amount",
    },
    "wallet.topup_custom_prompt": {
        "fa": "مبلغ دلخواه را به تومان بفرستید (بین {min} تا {max}):",
        "ar": "أرسل المبلغ المطلوب بالتومان (بين {min} و{max}):",
        "en": "Send the amount in toman (between {min} and {max}):",
    },
    "wallet.topup_custom_invalid": {
        "fa": "لطفاً یک عدد معتبر بین {min} تا {max} تومان بفرستید.",
        "ar": "أرسل رقماً صحيحاً بين {min} و{max} تومان.",
        "en": "Please send a valid number between {min} and {max} toman.",
    },
    "wallet.overview": {
        "fa": "💰 کیف پول شما\n\n"
        "موجودی پرداختی: {balance} تومان\n"
        "اعتبار هدیه: {credit} تومان\n"
        "پلن: {plan}\n\n"
        "برای شارژ فقط یکی از مبلغ‌های زیر را لمس کنید. بعد از پرداخت موفق، "
        "مبلغ خودکار به کیف پولتان اضافه می‌شود.",
        "ar": "💰 محفظتك\n\n"
        "الرصيد المدفوع: {balance} تومان\n"
        "رصيد الهدية: {credit} تومان\n"
        "الخطة: {plan}\n\n"
        "للشحن اضغط فقط أحد المبالغ أدناه. بعد نجاح الدفع، يُضاف المبلغ تلقائياً إلى محفظتك.",
        "en": "💰 Your wallet\n\n"
        "Paid balance: {balance} toman\n"
        "Gift credit: {credit} toman\n"
        "Plan: {plan}\n\n"
        "To top up, just tap one of the amounts below. After a successful payment, the amount is added to your wallet automatically.",
    },
    "wallet.no_invoices": {
        "fa": "هنوز فاکتور یا رسیدی برای شما ثبت نشده است.", "ar": "لم يتم تسجيل أي فاتورة أو إيصال لك بعد.",
        "en": "No invoice or receipt has been recorded for you yet.",
    },
    "wallet.invoice_kind.TOPUP": {"fa": "شارژ کیف پول", "ar": "شحن المحفظة", "en": "Wallet top-up"},
    "wallet.invoice_kind.KHATM_CREATION": {"fa": "ساخت ختم", "ar": "إنشاء ختمة", "en": "Khatm creation"},
    "wallet.invoice_kind.PURCHASE": {"fa": "خرید", "ar": "شراء", "en": "Purchase"},
    "wallet.invoice_status.PAID": {"fa": "پرداخت‌شده ✅", "ar": "مدفوعة ✅", "en": "Paid ✅"},
    "wallet.invoice_status.REFUNDED": {"fa": "بازپرداخت‌شده ↩️", "ar": "مُستردة ↩️", "en": "Refunded ↩️"},
    "wallet.invoices_header": {
        "fa": "🧾 آخرین فاکتورها و رسیدهای شما", "ar": "🧾 آخر فواتيرك وإيصالاتك", "en": "🧾 Your recent invoices and receipts",
    },
    "wallet.invoice_line": {
        "fa": "\n{kind} — {amount} تومان\nوضعیت: {status}\nشماره: {number}",
        "ar": "\n{kind} — {amount} تومان\nالحالة: {status}\nالرقم: {number}",
        "en": "\n{kind} — {amount} toman\nStatus: {status}\nNumber: {number}",
    },
    "wallet.invalid_amount": {"fa": "مبلغ نامعتبر است.", "ar": "المبلغ غير صالح.", "en": "The amount isn't valid."},
    "wallet.amount_not_selectable": {
        "fa": "این مبلغ قابل انتخاب نیست.", "ar": "هذا المبلغ غير قابل للاختيار.", "en": "This amount isn't a selectable option.",
    },
    "wallet.gateway_not_configured": {
        "fa": "درگاه شارژ هنوز از طرف مدیر فعال نشده است. لطفاً کمی بعد دوباره امتحان کنید.",
        "ar": "لم يفعّل المدير بوابة الشحن بعد. يرجى المحاولة مرة أخرى بعد قليل.",
        "en": "The top-up gateway hasn't been enabled by an admin yet. Please try again shortly.",
    },
    "wallet.topup_description": {
        "fa": "شارژ کیف پول ختم‌ساز - {amount} تومان", "ar": "شحن محفظة ختم‌ساز - {amount} تومان",
        "en": "KhatmSaz wallet top-up - {amount} toman",
    },
    "wallet.gateway_unreachable": {
        "fa": "فعلاً ارتباط با درگاه پرداخت برقرار نشد. مبلغی کم نشده؛ لطفاً چند دقیقه دیگر دوباره امتحان کنید.",
        "ar": "تعذّر الاتصال بوابة الدفع حالياً. لم يُخصم أي مبلغ؛ يرجى المحاولة بعد بضع دقائق.",
        "en": "Couldn't reach the payment gateway right now. Nothing was charged; please try again in a few minutes.",
    },
    "wallet.pay_button": {
        "fa": "پرداخت امن {amount} تومان", "ar": "دفع آمن {amount} تومان", "en": "Secure payment {amount} toman",
    },
    "wallet.final_topup_step": {
        "fa": "مرحلهٔ آخر شارژ کیف پول\n\n"
        "مبلغ: {amount} تومان\n"
        "۱) اگر درگاه با VPN باز نمی‌شود، لینک را باز کنید و پیش از پرداخت VPN را خاموش کنید.\n"
        "۲) پرداخت بانکی را تا پایان کامل کنید و صفحه را نبندید.\n"
        "۳) تغییر IP یا خاموش‌کردن VPN پرداخت را از حساب شما جدا نمی‌کند؛ بعد از بازگشت موفق به ختم‌ساز و دیدن پیام «کیف پول شارژ شد»، موجودی ثبت شده است.\n\n"
        "اگر پرداخت را لغو کنید یا ناموفق باشد، کیف پول تغییر نمی‌کند.",
        "ar": "الخطوة الأخيرة لشحن المحفظة\n\n"
        "المبلغ: {amount} تومان\n"
        "١) اضغط زر الدفع الآمن.\n"
        "٢) أكمل الدفع البنكي.\n"
        "٣) بعد رؤية رسالة «تم شحن المحفظة»، ارجع إلى البوت واضغط زر «عرض الرصيد» مرة أخرى.\n\n"
        "إذا ألغيت الدفع أو فشل، لن تتغير المحفظة.",
        "en": "Final step to top up your wallet\n\n"
        "Amount: {amount} toman\n"
        "1) Tap the secure payment button.\n"
        "2) Complete the bank payment.\n"
        "3) After seeing “wallet topped up”, come back to the bot and tap “View balance” again.\n\n"
        "If you cancel or the payment fails, your wallet won't change.",
    },
    "wallet.link_created": {
        "fa": "لینک پرداخت ساخته شد ✅", "ar": "تم إنشاء رابط الدفع ✅", "en": "Payment link created ✅",
    },

    # --- change_phone.py (2026-09-20) ---
    "change_phone.complete_profile_first": {
        "fa": "برای ساخت ختم، اول مشخصات کوتاه سازنده را کامل می‌کنیم. "
        "نام، شماره، استان، شهر و جنسیت را قدم‌به‌قدم می‌پرسم 🌱",
        "ar": "لإنشاء ختمة، نكمل أولاً بيانات المنشئ القصيرة. سأسألك الاسم والرقم والمحافظة "
        "والمدينة والجنس خطوة بخطوة 🌱",
        "en": "To create a khatm, we'll first complete your short creator profile. I'll ask for your name, "
        "phone, province, city, and gender step by step 🌱",
    },
    "change_phone.phone_taken": {
        "fa": "این شماره قبلاً برای حساب دیگری تأیید شده است. اگر حساب قبلی متعلق به خودتان است، "
        "با /link_account آن را امن وصل کنید؛ در غیر این صورت شمارهٔ پروفایل را اصلاح کنید.",
        "ar": "هذا الرقم موثّق مسبقاً لحساب آخر. إذا كان ذلك الحساب لك، اربطه بأمان عبر /link_account؛ "
        "وإلا صحّح رقم ملفك الشخصي.",
        "en": "This number is already verified for another account. If that account is yours, link it "
        "securely with /link_account; otherwise correct your profile's phone number.",
    },
    "change_phone.currently_unavailable": {
        "fa": "فعلاً امکان تأیید این شماره نیست. شمارهٔ پروفایل را بررسی و دوباره تلاش کنید.",
        "ar": "لا يمكن توثيق هذا الرقم حالياً. تحقق من رقم ملفك الشخصي وحاول مرة أخرى.",
        "en": "This number can't be verified right now. Check your profile's phone number and try again.",
    },
    "change_phone.manual_review_creator": {
        "fa": "چون شمارهٔ شما خارج از ایران است، پیامک کاوه‌نگار ارسال نمی‌شود. "
        "درخواست تأیید دستی برای مدیریت ثبت شد ✅\n\n"
        "فقط یک بار نیاز به تأیید دارید. بعد از تأیید مدیریت، پیام و دکمهٔ ادامه برایتان فرستاده می‌شود.",
        "ar": "بما أن رقمك خارج إيران، لن تُرسل رسالة كافينيجار. تم تسجيل طلب التوثيق اليدوي للإدارة ✅\n\n"
        "تحتاج للتوثيق مرة واحدة فقط. بعد رسالة تأكيد الإدارة، اضغط زر «إنشاء ختمة جديدة» مرة أخرى.",
        "en": "Since your number is outside Iran, no Kavenegar SMS is sent. A manual-review request was "
        "logged for an admin ✅\n\nYou only need this once. After the admin's confirmation, tap "
        "“Create a new khatm” again.",
    },
    "change_phone.sms_gateway_down_creator": {
        "fa": "برای ساخت ختم باید شمارهٔ سازنده تأیید شود، اما ارسال پیامک فعلاً روی سرور فعال نیست. "
        "هیچ مبلغی کم و هیچ ختمی ساخته نشد. بعد از فعال‌شدن پنل پیامکی دوباره تلاش کنید.",
        "ar": "لإنشاء ختمة يجب توثيق رقم المنشئ، لكن إرسال الرسائل غير مفعّل على الخادم حالياً. "
        "لم يُخصم أي مبلغ ولم تُنشأ أي ختمة. حاول مرة أخرى بعد تفعيل لوحة الرسائل.",
        "en": "Creating a khatm requires verifying the creator's phone, but SMS sending isn't enabled on "
        "the server right now. Nothing was charged and no khatm was created. Try again once the SMS "
        "panel is enabled.",
    },
    "change_phone.otp_sms_text": {
        "fa": "رمز تأیید سازنده ختم‌ساز: {code}\nاعتبار: ۵ دقیقه",
        "ar": "رمز توثيق منشئ ختم‌ساز: {code}\nصالح لمدة ۵ دقائق",
        "en": "KhatmSaz creator verification code: {code}\nValid for 5 minutes",
    },
    "change_phone.ask_creator_otp": {
        "fa": "برای اینکه بتوانید ختم بسازید، شمارهٔ ثبت‌شده باید یک بار تأیید شود. "
        "رمز شش‌رقمی ارسال شد؛ آن را همین‌جا بفرستید 🌱",
        "ar": "لتتمكن من إنشاء ختمة، يجب توثيق رقمك المسجَّل مرة واحدة. تم إرسال رمز من ستة أرقام؛ "
        "أرسله هنا 🌱",
        "en": "To be able to create a khatm, your registered number needs to be verified once. A 6-digit "
        "code was sent; send it here 🌱",
    },
    "change_phone.request_admin_after_expiry": {
        "fa": "🧑‍💼 پیامک نرسید؛ درخواست بررسی شماره",
        "ar": "🧑‍💼 لم يصل الرمز؟ اطلب مراجعة الإدارة بعد 5 دقائق",
        "en": "🧑‍💼 No code? Ask an admin after 5 minutes",
    },
    "change_phone.manual_wait_five_minutes": {
        "fa": "هنوز ۵ دقیقهٔ اعتبار کد تمام نشده است. کمی صبر کنید و بعد دوباره همین دکمه را بزنید.",
        "ar": "لم تنتهِ صلاحية الرمز لمدة 5 دقائق بعد. انتظر قليلاً ثم اضغط الزر مرة أخرى.",
        "en": "The code's 5-minute window has not ended yet. Wait a little and tap again.",
    },
    "change_phone.manual_submitted_after_expiry": {
        "fa": "درخواست بررسی شماره برای مدیر فرستاده شد ✅ نتیجهٔ بررسی همین‌جا برایتان می‌آید؛ اگر تأیید شود، دکمهٔ ادامه هم نمایش داده می‌شود.",
        "ar": "أُرسل طلب توثيق الرقم إلى الإدارة ✅ بعد المراجعة ستصلك رسالة وزر متابعة.",
        "en": "Your phone verification request was sent to an admin ✅ After review, you'll receive a confirmation and Continue button.",
    },
    "change_phone.otp_expired_admin_available": {
        "fa": "مهلت ۵ دقیقه‌ای این کد تمام شد. اگر پیامک به دستتان نرسیده، با دکمهٔ زیر از مدیر درخواست تأیید شماره کنید.",
        "ar": "انتهت مهلة الرمز البالغة 5 دقائق. إذا لم تصلك الرسالة، اطلب من الإدارة توثيق الرقم بالزر أدناه.",
        "en": "This code's 5-minute window has ended. If the SMS never arrived, use the button below to request admin verification.",
    },
    "change_phone.manual_invalid": {
        "fa": "این درخواست دیگر معتبر نیست. دوباره فرایند تأیید شماره را شروع کنید.",
        "ar": "هذا الطلب لم يعد صالحًا. ابدأ توثيق الرقم من جديد.",
        "en": "This request is no longer valid. Start phone verification again.",
    },
    "change_phone.dev_otp_hint": {
        "fa": "\n\nحالت توسعه فعال است؛ رمز آزمایشی: {code}", "ar": "\n\nوضع التطوير مفعّل؛ الرمز التجريبي: {code}",
        "en": "\n\nDev mode is on; test code: {code}",
    },
    "change_phone.already_verified": {
        "fa": "شمارهٔ شما از قبل تأیید شده است ✅ می‌توانید ختم جدید بسازید.",
        "ar": "رقمك موثّق مسبقاً ✅ يمكنك إنشاء ختمة جديدة.",
        "en": "Your number is already verified ✅ You can create a new khatm.",
    },
    "change_phone.begin_prompt": {
        "fa": "📱 تغییر شماره موبایل\n\n"
        "شمارهٔ جدیدتان را بفرستید؛ مثل 09121234567 یا برای خارج از ایران با کد کشور مثل +49151… . "
        "برای شمارهٔ ایران رمز شش‌رقمی ارسال می‌شود؛ شمارهٔ خارجی یک بار برای تأیید دستی مدیریت می‌رود.\n\n"
        "خیالتان راحت: ختم‌ها، سهم‌ها، کیف پول، سوابق انجام و حساب تلگرام/بله شما حذف یا جابه‌جا نمی‌شوند. "
        "شماره فقط بعد از واردکردن رمز درست عوض می‌شود. اگر منصرف شدید یکی از دکمه‌های منوی پایین را بزنید.",
        "ar": "📱 تغيير رقم الجوال\n\n"
        "أرسل رقمك الجديد؛ مثل 09121234567 أو لخارج إيران بكود الدولة مثل +49151… . للرقم الإيراني "
        "يُرسل رمز من ستة أرقام؛ الرقم الأجنبي يذهب مرة واحدة للتوثيق اليدوي من الإدارة.\n\n"
        "اطمئن: ختماتك وحصصك ومحفظتك وسجلاتك وحساب تيليجرام/بله لن تُحذف أو تُنقل. يتغير الرقم "
        "فقط بعد إدخال الرمز الصحيح. إذا عدلت عن رأيك اضغط أحد أزرار القائمة أدناه.",
        "en": "📱 Change phone number\n\n"
        "Send your new number; like 09121234567, or with a country code for outside Iran like "
        "+49151… . An Iranian number gets a 6-digit code; a foreign number goes to an admin for a "
        "one-time manual review.\n\n"
        "Don't worry: your khatms, portions, wallet, history, and Telegram/Bale account aren't "
        "deleted or moved. The number only changes after you enter the correct code. If you change "
        "your mind, tap one of the menu buttons below.",
    },
    "change_phone.phone_taken_secure": {
        "fa": "این شماره قبلاً برای حساب دیگری تأیید شده و برای امنیت قابل استفاده نیست. "
        "اگر آن حساب متعلق به خودتان است، از /link_account استفاده کنید.",
        "ar": "هذا الرقم موثّق مسبقاً لحساب آخر ولا يمكن استخدامه لأسباب أمنية. "
        "إذا كان ذلك الحساب لك، استخدم /link_account.",
        "en": "This number is already verified for another account and can't be used for security "
        "reasons. If that account is yours, use /link_account.",
    },
    "change_phone.already_verified_same": {
        "fa": "همین شماره از قبل برای حساب شما تأیید شده و نیازی به تغییر نیست.",
        "ar": "هذا الرقم موثّق مسبقاً لحسابك ولا حاجة لتغييره.",
        "en": "This exact number is already verified for your account and doesn't need changing.",
    },
    "change_phone.invalid_or_locked": {
        "fa": "شماره معتبر نبود یا حساب شما فعلاً امکان تغییر شماره ندارد. دوباره /change_phone را بزنید.",
        "ar": "الرقم غير صالح أو لا يمكن لحسابك تغيير الرقم حالياً. أرسل /change_phone مرة أخرى.",
        "en": "The number wasn't valid, or your account can't change its number right now. Send "
        "/change_phone again.",
    },
    "change_phone.manual_review_change": {
        "fa": "شمارهٔ جدید خارج از ایران است؛ بنابراین درخواست تغییر برای بررسی دستی مدیریت ثبت شد ✅\n"
        "تا قبل از تأیید، شماره و همهٔ سوابق فعلی شما بدون تغییر می‌مانند.",
        "ar": "الرقم الجديد خارج إيران؛ لذلك سُجِّل طلب التغيير للمراجعة اليدوية من الإدارة ✅\n"
        "حتى الموافقة، يبقى رقمك وكل سجلاتك الحالية دون تغيير.",
        "en": "The new number is outside Iran, so the change request was logged for admin manual "
        "review ✅\nUntil approved, your current number and all your records stay unchanged.",
    },
    "change_phone.otp_sms_text_change": {
        "fa": "رمز تغییر شماره ختم‌ساز: {code}\nاعتبار: ۵ دقیقه",
        "ar": "رمز تغيير رقم ختم‌ساز: {code}\nصالح لمدة ۵ دقائق",
        "en": "KhatmSaz phone-change code: {code}\nValid for 5 minutes",
    },
    "change_phone.sms_gateway_down_change": {
        "fa": "ارسال پیامک فعلاً روی سرور فعال نیست؛ شماره و هیچ سابقه‌ای تغییر نکرد. "
        "بعد از فعال‌شدن پنل پیامکی دوباره /change_phone را بزنید.",
        "ar": "إرسال الرسائل غير مفعّل على الخادم حالياً؛ لم يتغير الرقم ولا أي سجل. "
        "أرسل /change_phone مرة أخرى بعد تفعيل لوحة الرسائل.",
        "en": "SMS sending isn't enabled on the server right now; your number and history are "
        "unchanged. Send /change_phone again once the SMS panel is enabled.",
    },
    "change_phone.ask_change_otp": {
        "fa": "رمز شش‌رقمی به شمارهٔ جدید ارسال شد. رمز را همین‌جا بفرستید؛ ۵ دقیقه اعتبار دارد.",
        "ar": "أُرسل رمز من ستة أرقام إلى الرقم الجديد. أرسل الرمز هنا؛ صالح لمدة ۵ دقائق.",
        "en": "A 6-digit code was sent to the new number. Send it here; it's valid for 5 minutes.",
    },
    "change_phone.code_must_be_six_digits": {
        "fa": "رمز باید دقیقاً شش رقم باشد. لطفاً دوباره بفرستید.",
        "ar": "يجب أن يتكون الرمز من ستة أرقام بالضبط. يرجى إرساله مرة أخرى.",
        "en": "The code must be exactly 6 digits. Please send it again.",
    },
    "change_phone.otp_invalid_or_expired": {
        "fa": "رمز درست نبود، منقضی شده یا تغییر دیگر قابل انجام نیست. "
        "اگر فقط رمز را اشتباه زده‌اید دوباره بفرستید؛ بعد از پنج تلاش باید /change_phone را از اول بزنید.",
        "ar": "الرمز غير صحيح أو منتهي الصلاحية أو لم يعد التغيير ممكناً. "
        "إذا كنت أخطأت في كتابة الرمز فقط أرسله مرة أخرى؛ بعد خمس محاولات أرسل /change_phone من جديد.",
        "en": "The code was wrong, expired, or the change is no longer possible. If you just mistyped "
        "the code, send it again; after five attempts you'll need to start over with /change_phone.",
    },
    "change_phone.request_data_lost": {
        "fa": "اطلاعات این درخواست از بین رفته است. لطفاً /change_phone را دوباره بزنید.",
        "ar": "فُقدت بيانات هذا الطلب. يرجى إرسال /change_phone مرة أخرى.",
        "en": "This request's data was lost. Please send /change_phone again.",
    },
    "change_phone.creator_verified_success": {
        "fa": "شمارهٔ {phone} با موفقیت تأیید شد ✅\n"
        "حالا دکمهٔ «➕ ساخت ختم جدید» را بزنید؛ اطلاعات را خیلی ساده و مرحله‌به‌مرحله می‌پرسم.",
        "ar": "تم توثيق الرقم {phone} بنجاح ✅\n"
        "الآن اضغط زر «➕ إنشاء ختمة جديدة»؛ سأسألك المعلومات بشكل بسيط وخطوة بخطوة.",
        "en": "The number {phone} was verified successfully ✅\n"
        "Now tap “➕ Create a new khatm”; I'll ask for the details simply, step by step.",
    },
    "change_phone.number_changed_success": {
        "fa": "شماره با موفقیت به {phone} تغییر کرد ✅\n"
        "همهٔ ختم‌ها، سهم‌ها، موجودی کیف پول و سوابق قبلی شما بدون تغییر حفظ شده‌اند.",
        "ar": "تم تغيير الرقم بنجاح إلى {phone} ✅\n"
        "جميع ختماتك وحصصك ورصيد محفظتك وسجلاتك السابقة محفوظة دون تغيير.",
        "en": "Your number was successfully changed to {phone} ✅\n"
        "All your khatms, portions, wallet balance, and previous history are preserved unchanged.",
    },

    # --- account_link.py (2026-09-20) ---
    "account_link.begin_prompt": {
        "fa": "🔗 اتصال حساب قبلی\n\n"
        "این گزینه برای وقتی است که قبلاً در تلگرام یا بله ثبت‌نام کرده‌اید و حالا با حساب/پیام‌رسان دیگری وارد شده‌اید.\n"
        "شماره‌ای را که در حساب قبلی ثبت کرده بودید بفرستید؛ مثل 09121234567.\n\n"
        "اگر حسابی با آن شماره وجود داشته باشد، یک رمز شش‌رقمی برای همان شماره ارسال می‌شود. "
        "تا رمز درست وارد نشود هیچ حسابی جابه‌جا نمی‌شود.",
        "ar": "🔗 ربط حساب سابق\n\n"
        "هذا الخيار لمن سجّل مسبقاً في تيليجرام أو بله وأصبح الآن يستخدم حساباً/تطبيق مراسلة آخر.\n"
        "أرسل الرقم الذي سجّلته في الحساب السابق؛ مثل 09121234567.\n\n"
        "إذا وُجد حساب بذلك الرقم، يُرسل رمز من ستة أرقام لنفس الرقم. لن يُنقل أي حساب حتى يُدخَل "
        "الرمز الصحيح.",
        "en": "🔗 Link a previous account\n\n"
        "This is for when you previously registered on Telegram or Bale and are now using a "
        "different account/messenger.\n"
        "Send the number you registered with on the previous account; like 09121234567.\n\n"
        "If an account with that number exists, a 6-digit code is sent to that same number. No "
        "account is moved until the correct code is entered.",
    },
    "account_link.no_account_found": {
        "fa": "امکان اتصال با این شماره پیدا نشد. شماره را دقیقاً مثل حساب قبلی بررسی کنید. "
        "اگر با این حساب جدید قبلاً ختم یا کیف پول ساخته‌اید، برای اتصال امن با پشتیبانی تماس بگیرید.",
        "ar": "تعذّر الربط بهذا الرقم. تحقق من الرقم بدقة كما في الحساب السابق. "
        "إذا كنت أنشأت ختمة أو محفظة بهذا الحساب الجديد مسبقاً، تواصل مع الدعم للربط الآمن.",
        "en": "Couldn't link with this number. Double-check the number matches the previous account "
        "exactly. If you've already created a khatm or wallet with this new account, contact support "
        "for a safe merge.",
    },
    "account_link.otp_sms_text": {
        "fa": "رمز اتصال حساب ختم‌ساز: {code}\nاعتبار: ۱۰ دقیقه",
        "ar": "رمز ربط حساب ختم‌ساز: {code}\nصالح لمدة ۱۰ دقائق",
        "en": "KhatmSaz account-link code: {code}\nValid for 10 minutes",
    },
    "account_link.sms_gateway_down": {
        "fa": "ارسال پیامک فعلاً روی سرور فعال نیست؛ هیچ تغییری در حساب‌ها انجام نشد. "
        "بعد از اتصال پنل پیامکی دوباره همین دستور را بزنید.",
        "ar": "إرسال الرسائل غير مفعّل على الخادم حالياً؛ لم يتغير أي شيء في الحسابات. "
        "أرسل هذا الأمر مرة أخرى بعد تفعيل لوحة الرسائل.",
        "en": "SMS sending isn't enabled on the server right now; no accounts were changed. Send this "
        "command again once the SMS panel is enabled.",
    },
    "account_link.ask_otp": {
        "fa": "رمز شش‌رقمی ارسال شد. آن را همین‌جا بفرستید. رمز فقط ۱۰ دقیقه اعتبار دارد.",
        "ar": "أُرسل رمز من ستة أرقام. أرسله هنا. الرمز صالح لمدة ۱۰ دقائق فقط.",
        "en": "A 6-digit code was sent. Send it here. The code is only valid for 10 minutes.",
    },
    "account_link.dev_otp_hint": {
        "fa": "\n\nحالت توسعه فعال است؛ رمز آزمایشی: {code}", "ar": "\n\nوضع التطوير مفعّل؛ الرمز التجريبي: {code}",
        "en": "\n\nDev mode is on; test code: {code}",
    },
    "account_link.code_must_be_six_digits": {
        "fa": "رمز باید دقیقاً شش رقم باشد. دوباره بفرستید.",
        "ar": "يجب أن يتكون الرمز من ستة أرقام بالضبط. أرسله مرة أخرى.",
        "en": "The code must be exactly 6 digits. Send it again.",
    },
    "account_link.default_display_name": {"fa": "دوست عزیز", "ar": "صديقنا العزيز", "en": "dear friend"},
    "account_link.otp_invalid_or_expired": {
        "fa": "رمز درست نبود، منقضی شده یا این اتصال دیگر قابل انجام نیست. "
        "اگر هنوز فرصت دارید دوباره رمز را وارد کنید؛ بعد از پنج تلاش باید /link_account را از اول بزنید.",
        "ar": "الرمز غير صحيح أو منتهي الصلاحية أو لم يعد هذا الربط ممكناً. "
        "إذا كانت لديك فرصة أدخل الرمز مرة أخرى؛ بعد خمس محاولات أرسل /link_account من جديد.",
        "en": "The code was wrong, expired, or this link can no longer be completed. If you still have "
        "attempts left, enter the code again; after five attempts you'll need to start over with "
        "/link_account.",
    },
    "account_link.data_lost": {
        "fa": "اطلاعات این اتصال دیگر در دسترس نیست. لطفاً /link_account را دوباره بزنید.",
        "ar": "بيانات هذا الربط لم تعد متاحة. يرجى إرسال /link_account مرة أخرى.",
        "en": "This link request's data is no longer available. Please send /link_account again.",
    },
    "account_link.success": {
        "fa": "حساب با موفقیت متصل شد ✅\nخوش برگشتید {name}. از این به بعد سابقهٔ قبلی‌تان در همین گفت‌وگو در دسترس است.",
        "ar": "تم ربط الحساب بنجاح ✅\nأهلاً بعودتك {name}. من الآن سجلك السابق متاح في هذه المحادثة.",
        "en": "Your account was linked successfully ✅\nWelcome back {name}. Your previous history is now available in this chat.",
    },

    # --- account.py (2026-09-20) ---
    "account.delete_button": {"fa": "✅ حذف حساب", "ar": "✅ حذف الحساب", "en": "✅ Delete account"},
    "account.cancel_button": {"fa": "لغو", "ar": "إلغاء", "en": "Cancel"},
    "account.delete_confirm_prompt": {
        "fa": "حذف حساب قابل بازگشت نیست. عضویت‌های آزاد بسته می‌شوند و اطلاعات شخصی پاک می‌شود؛ "
        "سابقهٔ ختم و تراکنش‌ها برای صحت گزارش باقی می‌ماند. ادامه می‌دهید؟",
        "ar": "حذف الحساب لا يمكن التراجع عنه. تُغلق العضويات المفتوحة وتُمحى بياناتك الشخصية؛ "
        "يبقى سجل الختمات والمعاملات لدقة التقارير. هل تريد المتابعة؟",
        "en": "Deleting your account can't be undone. Open memberships will be closed and your "
        "personal data erased; khatm and transaction history stays for reporting accuracy. Continue?",
    },
    "account.deletion_cancelled": {
        "fa": "حذف حساب لغو شد.", "ar": "تم إلغاء حذف الحساب.", "en": "Account deletion was cancelled.",
    },
    "account.not_found": {
        "fa": "حساب کاربری پیدا نشد.", "ar": "لم يتم العثور على الحساب.", "en": "Account wasn't found.",
    },
    "account.blocked_prefix": {
        "fa": "ابتدا تعیین تکلیف کنید: ", "ar": "يرجى تسوية ما يلي أولاً: ", "en": "Please resolve these first: ",
    },
    "account.blocked_committed_count": {
        "fa": "{count} عضویت تعهدی فعال", "ar": "{count} عضوية ملتزمة نشطة", "en": "{count} active committed membership(s)",
    },
    "account.blocked_active_created_count": {
        "fa": "{count} ختم فعال ساخته‌شده توسط شما", "ar": "{count} ختمة نشطة أنشأتها",
        "en": "{count} active khatm(s) you created",
    },
    "account.blocked_join_word": {"fa": " و ", "ar": " و ", "en": " and "},
    "account.deleted": {
        "fa": "حساب شما حذف شد و دیگر قابل استفاده نیست.", "ar": "تم حذف حسابك ولم يعد قابلاً للاستخدام.",
        "en": "Your account has been deleted and can no longer be used.",
    },
    "account.deleted_toast": {"fa": "حساب حذف شد.", "ar": "تم حذف الحساب.", "en": "Account deleted."},

    # --- creator_decisions.py: /khatm_decision is a deprecated stub since
    # the emergency-portion/miss-notification system it managed was removed
    # (owner decision, 2026-09-21) ---
    "creator_decisions.no_longer_available": {
        "fa": "این دستور دیگه فعال نیست. سهم‌های ازدست‌رفته دیگه نیاز به تصمیم شما ندارن — هر عضو، سهم بعدی‌ش رو خودش هر وقت آماده بود دریافت می‌کنه.",
        "ar": "هذا الأمر لم يعد متاحاً. الحصص الفائتة لم تعد بحاجة لقرار منك — كل عضو يحصل على حصته التالية عندما يكون جاهزاً.",
        "en": "This command is no longer available. Missed portions no longer need a creator decision — each member simply gets their next portion whenever they're ready.",
    },

    # --- khatm_request.py: submitter-facing part (2026-09-20) ---
    "khatm_request.submitted": {
        "fa": "درخواستتون ثبت شد ✅ به‌محض بررسی توسط مدیریت، بهتون خبر می‌دیم.",
        "ar": "تم تسجيل طلبك ✅ سنبلغك فور مراجعته من الإدارة.",
        "en": "Your request was submitted ✅ We'll let you know once it's reviewed by an admin.",
    },
    "khatm_request.attachment_saved": {
        "fa": "\nفایل ارسالی هم برای بررسی مدیریت ذخیره شد.", "ar": "\nتم حفظ الملف المرسل أيضاً لمراجعة الإدارة.",
        "en": "\nThe file you sent was also saved for admin review.",
    },
    "khatm_request.ask_description": {
        "fa": "لطفاً اسم و توضیح کوتاه ختمی را که در فهرست پیدا نکردید بنویسید.\n\n"
        "مثال: ختم دعای عهد؛ هر نفر روزی یک بار بخواند.",
        "ar": "يرجى كتابة اسم ووصف قصير للختمة التي لم تجدها في القائمة.\n\n"
        "مثال: ختمة دعاء العهد؛ يقرأها كل شخص مرة يومياً.",
        "en": "Please write the name and a short description of the khatm you couldn't find in the list.\n\n"
        "Example: Dua Ahd khatm; each person reads it once a day.",
    },
    "khatm_request.description_required": {
        "fa": "لطفاً اسم و یک توضیح کوتاه برای ختم بنویسید.", "ar": "يرجى كتابة اسم ووصف قصير للختمة.",
        "en": "Please write a name and a short description for the khatm.",
    },
    "khatm_request.ask_attachment": {
        "fa": "اگر فایل نمونه، متن یا صوت دارید، همین حالا ارسال کنید؛ در غیر این صورت «ندارم» بنویسید.",
        "ar": "إذا كان لديك ملف نموذجي أو نص أو صوت، أرسله الآن؛ وإلا اكتب «ليس لدي».",
        "en": "If you have a sample file, text, or audio, send it now; otherwise type “none”.",
    },
    "khatm_request.attachment_or_skip": {
        "fa": "یک فایل ارسال کنید یا فقط «ندارم» بنویسید.", "ar": "أرسل ملفاً أو اكتب «ليس لدي» فقط.",
        "en": "Send a file, or just type “none”.",
    },
    "khatm_request.usage_hint": {
        "fa": "از بخش راهنما ← ساخت ختم، دکمهٔ «درخواست نوع ختم جدید» را بزنید.",
        "ar": "من قسم المساعدة ← إنشاء ختمة، اضغط زر «طلب نوع ختمة جديد».",
        "en": "From Help → Create a khatm, tap “Request a new khatm type”.",
    },

    # --- khatm_request.py: notifications to the requester after admin
    # approves/rejects (in the requester's own language; the admin-side
    # typed commands themselves remain Persian, same treatment as admin.py) ---
    "khatm_request.approved_notice": {
        "fa": "درخواست ختمی که فرستاده بودید تایید شد 🎉\n«{description}»",
        "ar": "تمت الموافقة على طلب الختمة الذي أرسلته 🎉\n«{description}»",
        "en": "The khatm request you sent was approved 🎉\n“{description}”",
    },
    "khatm_request.admin_note_line": {
        "fa": "\n\nیادداشت مدیریت: {note}", "ar": "\n\nملاحظة الإدارة: {note}", "en": "\n\nAdmin's note: {note}",
    },
    "khatm_request.rejected_notice": {
        "fa": "درخواست ختمی که فرستاده بودید فعلاً امکان‌پذیر نیست.\n«{description}»",
        "ar": "طلب الختمة الذي أرسلته غير ممكن حالياً.\n«{description}»",
        "en": "The khatm request you sent isn't possible for now.\n“{description}”",
    },
    "khatm_request.reason_line": {
        "fa": "\n\nدلیل: {note}", "ar": "\n\nالسبب: {note}", "en": "\n\nReason: {note}",
    },

    # --- public_khatms.py (2026-09-20) ---
    "public_khatms.none_active": {
        "fa": "در حال حاضر ختم عمومی فعالی وجود ندارد.", "ar": "لا توجد ختمة عامة نشطة حالياً.",
        "en": "There's no active public khatm right now.",
    },
    "public_khatms.list_prompt": {
        "fa": "ختم‌های عمومی فعال:\nبرای مشاهده و عضویت، یکی را انتخاب کنید.",
        "ar": "الختمات العامة النشطة:\nاختر واحدة للعرض والانضمام.",
        "en": "Active public khatms:\nChoose one to view and join.",
    },
    "public_khatms.no_longer_available": {
        "fa": "این ختم دیگر عمومی و فعال نیست.", "ar": "هذه الختمة لم تعد عامة ونشطة.",
        "en": "This khatm is no longer public and active.",
    },
    "public_khatms.commitment_consent_prompt": {
        "fa": "این ختم تعهدی است؛ با پذیرش آن، سهم تعیین‌شده را تا مهلت اعلام‌شده انجام می‌دهید.",
        "ar": "هذه ختمة ملتزمة؛ بقبولها تلتزم بإنجاز الحصة المحددة قبل الموعد المعلن.",
        "en": "This is a commitment khatm; by accepting it you pledge to complete your assigned portion by the announced deadline.",
    },

    # --- manual_phone_verification.py: requester-facing notification only
    # (admin review UI stays Persian, same treatment as admin.py) (2026-09-20) ---
    "manual_phone_verification.approved_notice": {
        "fa": "شمارهٔ خارج از کشور شما توسط مدیریت تأیید شد ✅\nاین تأیید دائمی است و حالا می‌توانید ختم بسازید.",
        "ar": "تم توثيق رقمك من خارج البلاد من الإدارة ✅\nهذا التوثيق دائم ويمكنك الآن إنشاء ختمة.",
        "en": "Your foreign phone number was verified by an admin ✅\nThis verification is permanent and you can now create a khatm.",
    },
    "manual_phone_verification.continue_button": {
        "fa": "✅ ادامهٔ فرایند",
        "ar": "✅ متابعة العملية",
        "en": "✅ Continue",
    },
    "manual_phone_verification.rejected_notice": {
        "fa": "درخواست تأیید شمارهٔ شما رد شد. لطفاً شماره و مشخصات پروفایل را بررسی و دوباره درخواست دهید.",
        "ar": "تم رفض طلب توثيق رقمك. يرجى مراجعة الرقم وبيانات ملفك الشخصي وإعادة الطلب.",
        "en": "Your phone verification request was rejected. Please check your number and profile details and request again.",
    },

    # --- devotional.py (2026-09-20) ---
    "devotional.usage": {
        "fa": "فرمت درست: /devotional ‹slug›", "ar": "الصيغة الصحيحة: /devotional ‹slug›",
        "en": "Correct format: /devotional ‹slug›",
    },
    "devotional.not_found": {
        "fa": "این دعا یا زیارت در کتابخانه پیدا نشد.", "ar": "لم يتم العثور على هذا الدعاء أو الزيارة في المكتبة.",
        "en": "This dua or ziyarat wasn't found in the library.",
    },
    "devotional.audio_caption": {
        "fa": "🎧 صوت کامل {title}", "ar": "🎧 الصوت الكامل لـ{title}", "en": "🎧 Full audio of {title}",
    },
    "devotional.audio_not_available_for_platform": {
        "fa": "صوت این محتوا هنوز برای پلتفرم شما ثبت نشده است.",
        "ar": "الصوت الخاص بهذا المحتوى لم يُسجَّل بعد لمنصتك.",
        "en": "The audio for this content hasn't been registered for your platform yet.",
    },
    "devotional.choose_reciter": {
        "fa": "این محتوا با چند قاری موجوده — یکی رو انتخاب کنید:",
        "ar": "هذا المحتوى متوفر بعدة قراء — اختر واحداً:",
        "en": "This content is available with more than one reciter — pick one:",
    },

    # --- legacy typed-command settings files (2026-09-20) ---
    # digest_settings.py
    "digest_settings.status_on": {"fa": "روشن", "ar": "مفعّل", "en": "On"},
    "digest_settings.status_off": {"fa": "خاموش", "ar": "معطّل", "en": "Off"},
    "digest_settings.current_status": {
        "fa": "Digest روزانه: {state}\nتغییر: /digest on یا /digest off",
        "ar": "الملخص اليومي: {state}\nللتغيير: /digest on أو /digest off",
        "en": "Daily digest: {state}\nTo change: /digest on or /digest off",
    },
    "digest_settings.usage": {
        "fa": "فرمت درست: /digest on یا /digest off", "ar": "الصيغة الصحيحة: /digest on أو /digest off",
        "en": "Correct format: /digest on or /digest off",
    },
    "digest_settings.turned_on": {"fa": "Digest روزانه روشن شد ✅", "ar": "تم تفعيل الملخص اليومي ✅", "en": "Daily digest turned on ✅"},
    "digest_settings.turned_off": {"fa": "Digest روزانه خاموش شد ✅", "ar": "تم إيقاف الملخص اليومي ✅", "en": "Daily digest turned off ✅"},

    # font_settings.py
    "font_settings.usage": {
        "fa": "فرمت درست: /font normal یا /font large", "ar": "الصيغة الصحيحة: /font normal أو /font large",
        "en": "Correct format: /font normal or /font large",
    },
    "font_settings.label_normal": {"fa": "معمولی", "ar": "عادي", "en": "Normal"},
    "font_settings.label_large": {"fa": "درشت", "ar": "كبير", "en": "Large"},
    "font_settings.saved": {
        "fa": "اندازه متن روی «{label}» تنظیم شد ✅", "ar": "تم ضبط حجم الخط على «{label}» ✅",
        "en": "Text size set to “{label}” ✅",
    },

    # language_settings.py
    "language_settings.label.fa": {"fa": "فارسی", "ar": "الفارسية", "en": "Persian"},
    "language_settings.label.ar": {"fa": "العربية", "ar": "العربية", "en": "Arabic"},
    "language_settings.label.en": {"fa": "English", "ar": "الإنجليزية", "en": "English"},
    "language_settings.current": {
        "fa": "زبان فعلی شما: {label} ({code})\nتغییر زبان: /language fa یا /language ar یا /language en",
        "ar": "لغتك الحالية: {label} ({code})\nلتغيير اللغة: /language fa أو /language ar أو /language en",
        "en": "Your current language: {label} ({code})\nTo change: /language fa, /language ar, or /language en",
    },
    "language_settings.invalid": {
        "fa": "زبان معتبر نیست. انتخاب کنید: fa، ar یا en", "ar": "اللغة غير صالحة. اختر: fa أو ar أو en",
        "en": "Not a valid language. Choose: fa, ar, or en",
    },
    "language_settings.saved": {
        "fa": "زبان شما روی {label} تنظیم شد ✅", "ar": "تم ضبط لغتك على {label} ✅", "en": "Your language was set to {label} ✅",
    },

    # reciter_settings.py
    "reciter_settings.usage": {
        "fa": "قاری را با شناسه انتخاب کنید: /reciter [شناسه]\nگزینه‌ها: {options}",
        "ar": "اختر القارئ بمعرفه: /reciter [المعرف]\nالخيارات: {options}",
        "en": "Choose a reciter by id: /reciter [id]\nOptions: {options}",
    },
    "reciter_settings.invalid": {
        "fa": "شناسه قاری معتبر نیست. برای دیدن گزینه‌ها /reciter را بفرستید.",
        "ar": "معرف القارئ غير صالح. أرسل /reciter لرؤية الخيارات.",
        "en": "That reciter id isn't valid. Send /reciter to see the options.",
    },
    "reciter_settings.saved": {
        "fa": "قاری محبوب شما روی «{name}» تنظیم شد ✅", "ar": "تم ضبط قارئك المفضل على «{name}» ✅",
        "en": "Your favorite reciter was set to “{name}” ✅",
    },

    # reminder_settings.py
    "reminder_settings.turned_off": {
        "fa": "یادآوری‌های تعهدی شما خاموش شد. برای روشن‌کردن: /reminder 9",
        "ar": "تم إيقاف تذكيرات التزاماتك. للتفعيل: /reminder 9",
        "en": "Your commitment reminders were turned off. To turn on: /reminder 9",
    },
    "reminder_settings.usage": {
        "fa": "ساعت را بین ۰ تا ۲۳ بفرستید؛ مثال: /reminder ۸\nخاموش‌کردن: /reminder off",
        "ar": "أرسل ساعة بين ۰ و۲۳؛ مثال: /reminder 8\nللإيقاف: /reminder off",
        "en": "Send an hour between 0 and 23; example: /reminder 8\nTo turn off: /reminder off",
    },
    "reminder_settings.saved": {
        "fa": "ساعت یادآوری تعهدهای شما روی {hour}:00 تنظیم شد ✅", "ar": "تم ضبط ساعة تذكير التزاماتك على {hour}:00 ✅",
        "en": "Your commitment reminder hour was set to {hour}:00 ✅",
    },

    # sms_settings.py
    "sms_settings.usage": {
        "fa": "فرمت درست: /sms on یا /sms off", "ar": "الصيغة الصحيحة: /sms on أو /sms off",
        "en": "Correct format: /sms on or /sms off",
    },
    "sms_settings.on_redirect": {
        "fa": "پیامک یادآوری فقط با خرید اشتراک فعال می‌شه. از «{settings_button}» → «📩 پیامک یادآوری» یکی از گزینه‌های اشتراک رو بخرید.",
        "ar": "تُفعَّل رسائل التذكير فقط بشراء اشتراك. من «{settings_button}» ← «📩 رسائل التذكير» اشترِ أحد خيارات الاشتراك.",
        "en": "SMS reminders only turn on after buying a subscription. From “{settings_button}” → “📩 SMS reminders”, buy one of the subscription options.",
    },
    "sms_settings.turned_off": {
        "fa": "دریافت SMS خاموش شد ✅", "ar": "تم إيقاف استقبال الرسائل ✅", "en": "SMS receiving turned off ✅",
    },

    # timezone_settings.py
    "timezone_settings.current": {
        "fa": "منطقه زمانی فعلی شما: {timezone}\nبرای تغییر: /timezone Asia/Tehran",
        "ar": "منطقتك الزمنية الحالية: {timezone}\nللتغيير: /timezone Asia/Tehran",
        "en": "Your current timezone: {timezone}\nTo change: /timezone Asia/Tehran",
    },
    "timezone_settings.invalid": {
        "fa": "منطقه زمانی معتبر نیست. نمونه: /timezone Asia/Tehran",
        "ar": "المنطقة الزمنية غير صالحة. مثال: /timezone Asia/Tehran",
        "en": "Not a valid timezone. Example: /timezone Asia/Tehran",
    },
    # --- start.py: join-invite preview message (2026-09-20, owner
    # complaint: the invite text was unappealing and didn't explain what
    # the khatm actually is or what committing to it means) ---
    "join.preview.header": {"fa": "معرفی ختم", "ar": "تعريف الختمة", "en": "Khatm introduction"},
    "join.preview.title": {"fa": "عنوان: {title}", "ar": "العنوان: {title}", "en": "Title: {title}"},
    "join.preview.creator": {"fa": "\nسازنده: {creator}", "ar": "\nالمنشئ: {creator}", "en": "\nCreator: {creator}"},
    "join.preview.niyyat": {"fa": "\nنیت: {niyyat}", "ar": "\nالنية: {niyyat}", "en": "\nIntention: {niyyat}"},
    "join.preview.type_quran": {
        "fa": "ختم قرآن (صفحه‌به‌صفحه)", "ar": "ختمة القرآن (صفحة بصفحة)", "en": "Quran khatm (page by page)",
    },
    "join.preview.type_salawat": {"fa": "صلوات", "ar": "صلوات", "en": "Salawat"},
    "join.preview.type_dua": {"fa": "دعا یا زیارت", "ar": "دعاء أو زيارة", "en": "Dua or Ziyarat"},
    "join.preview.type_laan": {"fa": "لعن", "ar": "لعن", "en": "La'an"},
    "join.preview.type_line": {
        "fa": "\n{icon} نوع ختم: {type}", "ar": "\n{icon} نوع الختمة: {type}", "en": "\n{icon} Khatm type: {type}",
    },
    "join.preview.type_line_with_category": {
        "fa": "\n{icon} نوع ختم: {type} — {category}", "ar": "\n{icon} نوع الختمة: {type} — {category}",
        "en": "\n{icon} Khatm type: {type} — {category}",
    },
    "join.preview.mode_commitment_quran": {
        "fa": "\n🔒 حالت: تعهدی — بعد از عضویت، یک سهم مشخص از قرآن می‌گیرید و متعهد می‌شید تا مهلت روزانه بخونیدش. "
        "اگه یک روز نخونید، ختم منتظرتون می‌مونه — این تعهد واقعاً روی پیشرفت کل ختم اثر می‌ذاره.",
        "ar": "\n🔒 الحالة: ملتزمة — بعد الانضمام تحصل على حصة محددة من القرآن وتلتزم بقراءتها قبل الموعد اليومي. "
        "إذا فاتك يوم، تنتظرك الختمة — هذا الالتزام يؤثر فعلاً على تقدم الختمة كلها.",
        "en": "\n🔒 Mode: Commitment — after joining, you get a specific Quran portion and pledge to read it "
        "by the daily deadline. If you miss a day, the khatm waits on you — this commitment really does "
        "affect the whole khatm's progress.",
    },
    "join.preview.mode_open_quran": {
        "fa": "\n🌿 حالت: آزاد — هیچ سهم مشخصی ندارید؛ هرچند صفحه که خواستید، هروقت خواستید می‌خونید.",
        "ar": "\n🌿 الحالة: مفتوحة — لا توجد حصة محددة لك؛ اقرأ أي عدد من الصفحات وفي أي وقت تريد.",
        "en": "\n🌿 Mode: Open — you have no fixed portion; read as many pages as you want, whenever you want.",
    },
    "join.preview.mode_commitment_quantified": {
        "fa": "\n🔒 حالت: تعهدی — با عضویت، متعهد می‌شید {count} {unit} انجام بدید.",
        "ar": "\n🔒 الحالة: ملتزمة — بالانضمام تلتزم بإنجاز {count} {unit}.",
        "en": "\n🔒 Mode: Commitment — by joining, you pledge to complete {count} {unit}.",
    },
    "join.preview.mode_open_generic": {
        "fa": "\n🌿 حالت: آزاد — هیچ تعهدی نیست؛ هرکس هرچقدر خواست مشارکت می‌کنه.",
        "ar": "\n🌿 الحالة: مفتوحة — لا يوجد التزام؛ كل شخص يشارك بقدر ما يريد.",
        "en": "\n🌿 Mode: Open — there's no pledge; everyone contributes as much as they want.",
    },
    "join.preview.mode_commitment_generic": {
        "fa": "\n🔐 حالت: تعهدی — مقدار یا برنامهٔ انتخاب‌شده تا زمان انجام برای شما ثبت می‌ماند.",
        "ar": "\n🔐 الوضع: التزام — يبقى المقدار أو البرنامج المختار مسجلاً حتى إنجازه.",
        "en": "\n🔐 Mode: commitment — your selected amount or schedule remains recorded until completion.",
    },
    "join.private_request_creator_notice": {
        "fa": "درخواست عضویت در ختم خصوصی «{title}»\n\nنام: {name}\nشماره تماس: {phone}\nشناسه پیام‌رسان: {identities}",
        "ar": "طلب انضمام إلى الختمة الخاصة «{title}»\n\nالاسم: {name}\nرقم الاتصال: {phone}\nمعرّف المنصة: {identities}",
        "en": "Private khatm join request for “{title}”\n\nName: {name}\nPhone: {phone}\nPlatform ID: {identities}",
    },
    "join.preview.member_count": {
        "fa": "\nتعداد اعضای فعلی: {count}", "ar": "\nعدد الأعضاء الحاليين: {count}", "en": "\nCurrent member count: {count}",
    },
    "join.preview.welcome_text": {
        "fa": "\n\nپیام سازنده:\n{text}", "ar": "\n\nرسالة المنشئ:\n{text}", "en": "\n\nCreator's message:\n{text}",
    },
    "join.preview.cta": {
        "fa": "\n\nبرای عضویت، دکمهٔ زیر را بزنید. با باز کردن لینک هنوز عضو نشده‌اید.",
        "ar": "\n\nللانضمام، اضغط الزر أدناه. بفتح الرابط لم تنضم بعد.",
        "en": "\n\nTo join, tap the button below. Opening the link doesn't make you a member yet.",
    },

    "timezone_settings.saved": {
        "fa": "منطقه زمانی شما روی {timezone} تنظیم شد ✅", "ar": "تم ضبط منطقتك الزمنية على {timezone} ✅",
        "en": "Your timezone was set to {timezone} ✅",
    },

    # --- my_khatms.py: combined action-list keyboard (2026-09-20, owner
    # request to stop the message-burst and use a single list instead) ---
    "my_khatms.button.manage": {
        "fa": "🛠 مدیریت «{title}»", "ar": "🛠 إدارة «{title}»", "en": "🛠 Manage “{title}”",
    },
    "my_khatms.button.contribute": {
        "fa": "➕ ثبت مشارکت در «{title}»", "ar": "➕ تسجيل مشاركة في «{title}»", "en": "➕ Log a contribution in “{title}”",
    },
    "my_khatms.button.resume": {
        "fa": "▶️ ادامه تعهد در «{title}»", "ar": "▶️ استئناف الالتزام في «{title}»", "en": "▶️ Resume commitment in “{title}”",
    },
    "my_khatms.button.pause": {
        "fa": "⏸ توقف موقت در «{title}»", "ar": "⏸ إيقاف مؤقت في «{title}»", "en": "⏸ Pause in “{title}”",
    },
    "my_khatms.no_permission": {
        "fa": "این ختم متعلق به شما نیست.", "ar": "هذه الختمة ليست لك.", "en": "This khatm doesn't belong to you.",
    },
    "my_khatms.manage_header": {
        "fa": "🛠 مدیریت «{title}»", "ar": "🛠 إدارة «{title}»", "en": "🛠 Manage “{title}”",
    },

    # --- my_khatms.py: creator typed commands + advanced `cs:*` settings
    # tree (BACKLOG.md §3/§1 leftover — 2026-09-21). Applied the tone-guide
    # checklist (docs/ai/TONE_GUIDE_80YO_PERSONA.md, BACKLOG.md §19) while
    # translating: short sentences, no unexplained jargon, no blame in
    # error text, clear verbs. `/khatm_skip_today` and `/khatm_miss_policy`
    # were removed rather than translated — they configured the "امروز
    # نمی‌رسم"/miss-notice features that no longer exist (see the
    # emergency-portion removal, same date). ---
    "my_khatms.creator.account_not_found": {
        "fa": "حساب شما پیدا نشد. لطفاً یک بار «/start» را بفرستید.",
        "ar": "لم يتم العثور على حسابك. أرسل «/start» مرة واحدة من فضلك.",
        "en": "We couldn't find your account. Please send “/start” once.",
    },
    "my_khatms.creator.khatm_not_found": {
        "fa": "این ختم پیدا نشد یا مال شما نیست.",
        "ar": "لم يتم العثور على هذه الختمة أو أنها ليست لك.",
        "en": "This khatm wasn't found, or it isn't yours.",
    },
    "my_khatms.creator.invalid_khatm_id": {
        "fa": "شناسه‌ی ختم درست نیست.", "ar": "معرّف الختمة غير صحيح.", "en": "That khatm id isn't valid.",
    },
    "my_khatms.creator.settings_intro": {
        "fa": "⚙️ تنظیمات «{title}»\n\nهر گزینه را که لمس کنید، روشن یا خاموش می‌شود. ✅ یعنی روشن و 🚫 یعنی خاموش.\nاین کار سهم‌های ثبت‌شده و سابقهٔ اعضا را پاک نمی‌کند.",
        "ar": "⚙️ إعدادات «{title}»\n\nكل خيار تلمسه يتفعّل أو يتوقف. ✅ يعني مفعّل و🚫 يعني متوقف.\nهذا لا يمسح الحصص المسجَّلة ولا سجل الأعضاء.",
        "en": "⚙️ Settings for “{title}”\n\nTapping any option turns it on or off. ✅ means on, 🚫 means off.\nThis doesn't erase logged portions or member history.",
    },
    "web.creator.settings_target": {"fa": "هدف کل ختم", "ar": "الهدف الكلي", "en": "Total goal"},
    "web.creator.settings_target_hint": {"fa": "برای حفظ پیشرفت اعضا، تعداد فقط قابل افزایش است.", "ar": "لحفظ تقدم الأعضاء يمكن زيادة العدد فقط.", "en": "To preserve member progress, the goal can only be increased."},
    "web.creator.settings_visibility": {"fa": "روش عضویت", "ar": "طريقة الانضمام", "en": "Membership visibility"},
    "web.creator.settings_platforms": {"fa": "پیام‌رسان‌های مجاز", "ar": "المنصات المسموحة", "en": "Allowed platforms"},
    "web.creator.settings_tone": {"fa": "لحن یادآوری", "ar": "نبرة التذكير", "en": "Reminder tone"},
    "web.creator.settings_deadline_hour": {"fa": "ساعت پایان مهلت روزانه (۰ تا ۲۳)", "ar": "ساعة نهاية المهلة اليومية", "en": "Daily deadline hour (0–23)"},
    "web.creator.platform_both": {"fa": "تلگرام و بله", "ar": "تلگرام وبله", "en": "Telegram and Bale"},
    "web.creator.platform_telegram": {"fa": "فقط تلگرام", "ar": "تلگرام فقط", "en": "Telegram only"},
    "web.creator.platform_bale": {"fa": "فقط بله", "ar": "بله فقط", "en": "Bale only"},
    "my_khatms.creator.schedule_current": {
        "fa": "\n\n⏰ زمان‌بندی الان: {label}", "ar": "\n\n⏰ الجدولة الحالية: {label}",
        "en": "\n\n⏰ Current schedule: {label}",
    },
    "my_khatms.creator.schedule_label.none": {"fa": "بدون زمان‌بندی", "ar": "بدون جدولة", "en": "No schedule"},
    "my_khatms.creator.schedule_label.daily": {"fa": "هر روز", "ar": "كل يوم", "en": "Every day"},
    "my_khatms.creator.schedule_label.weekly": {"fa": "روزهای مشخصی از هفته", "ar": "أيام محددة من الأسبوع", "en": "Specific days of the week"},
    "my_khatms.creator.schedule_label.interval": {
        "fa": "هر {value} روز یک‌بار", "ar": "كل {value} أيام", "en": "Every {value} days",
    },
    "my_khatms.creator.schedule_label.date": {"fa": "تاریخ {value}", "ar": "بتاريخ {value}", "en": "On {value}"},
    "my_khatms.creator.schedule_label.unknown": {"fa": "نامشخص", "ar": "غير معروف", "en": "Not set"},
    "my_khatms.creator.quran_only": {
        "fa": "این تنظیم فقط برای ختم قرآن شماست.", "ar": "هذا الإعداد فقط لختمة القرآن الخاصة بك.",
        "en": "This setting is only for your Quran khatm.",
    },
    "my_khatms.creator.content_mode_prompt": {
        "fa": "📖 محتوای هر سهم قرآن چطور برای اعضا ارسال شود؟\n\n«خودکار» بهترین گزینه است: هر چیزی که در کتابخانه موجود باشد می‌فرستد. صدا فقط برای کسانی می‌رود که خودشان از تنظیماتشان روشنش کرده‌اند.",
        "ar": "📖 كيف تُرسَل كل حصة من القرآن للأعضاء؟\n\n«تلقائي» هو الخيار الأفضل: يرسل كل ما هو متوفر في المكتبة. الصوت يصل فقط لمن فعّله بنفسه من إعداداته.",
        "en": "📖 How should each Quran portion be sent to members?\n\n“Automatic” is the best choice — it sends whatever is available. Audio only goes to members who've turned it on themselves.",
    },
    "my_khatms.creator.open_only": {
        "fa": "این زمان‌بندی فقط برای ختم آزاد است.", "ar": "هذه الجدولة فقط للختمة المفتوحة.",
        "en": "This schedule is only for open khatms.",
    },
    "my_khatms.creator.schedule_prompt": {
        "fa": "⏰ اعضای ختم آزاد چه زمانی یادآوری مشارکت بگیرند؟\n\nاین فقط زمان ارسال پیام یادآوری را تنظیم می‌کند.",
        "ar": "⏰ متى يصل تذكير المشاركة لأعضاء الختمة المفتوحة؟\n\nهذا يضبط فقط وقت إرسال رسالة التذكير.",
        "en": "⏰ When should open-khatm members get their participation reminder?\n\nThis only sets when the reminder message is sent.",
    },
    "my_khatms.creator.schedule_invalid": {
        "fa": "این زمان‌بندی برای این ختم قابل ثبت نیست.", "ar": "لا يمكن تسجيل هذه الجدولة لهذه الختمة.",
        "en": "This schedule can't be saved for this khatm.",
    },
    "my_khatms.creator.schedule_saved": {
        "fa": "زمان‌بندی ذخیره شد ✅", "ar": "تم حفظ الجدولة ✅", "en": "Schedule saved ✅",
    },
    "my_khatms.creator.ask_schedule_date": {
        "fa": "تاریخ اولین یادآوری را به وقت تهران بنویسید.\n\nمثال دقیق: 2026-10-01\nتاریخ باید امروز یا بعد از امروز باشد.",
        "ar": "اكتب تاريخ أول تذكير بتوقيت طهران.\n\nمثال دقيق: 2026-10-01\nيجب أن يكون التاريخ اليوم أو بعده.",
        "en": "Write the date of the first reminder, Tehran time.\n\nExample format: 2026-10-01\nThe date must be today or later.",
    },
    "my_khatms.creator.end_at_not_allowed": {
        "fa": "این ختم نمی‌تواند پایان تاریخی داشته باشد.", "ar": "لا يمكن ضبط تاريخ انتهاء لهذه الختمة.",
        "en": "This khatm can't have a set end date.",
    },
    "my_khatms.creator.ask_end_at": {
        "fa": "تاریخ پایان را به وقت تهران بنویسید.\n\nمثال دقیق: 2026-10-01 23:00\nتاریخ باید بعد از الان باشد.",
        "ar": "اكتب تاريخ الانتهاء بتوقيت طهران.\n\nمثال دقيق: 2026-10-01 23:00\nيجب أن يكون بعد الآن.",
        "en": "Write the end date, Tehran time.\n\nExample format: 2026-10-01 23:00\nIt must be after right now.",
    },
    "my_khatms.creator.end_at_cannot_clear": {
        "fa": "پایان تاریخی این ختم قابل حذف نیست.", "ar": "لا يمكن حذف تاريخ انتهاء هذه الختمة.",
        "en": "This khatm's end date can't be removed.",
    },
    "my_khatms.creator.end_at_cleared": {
        "fa": "پایان تاریخی حذف شد ✅", "ar": "تم حذف تاريخ الانتهاء ✅", "en": "End date removed ✅",
    },
    "my_khatms.creator.edit_field_invalid": {
        "fa": "این گزینهٔ ویرایش وجود ندارد.", "ar": "خيار التعديل هذا غير موجود.", "en": "That edit option doesn't exist.",
    },
    "my_khatms.creator.active_only_edit": {
        "fa": "فقط ختم فعال خودتان قابل ویرایش است.", "ar": "يمكن تعديل ختمتك النشطة فقط.",
        "en": "Only your active khatm can be edited.",
    },
    "my_khatms.creator.ask_new_title": {
        "fa": "عنوان جدید را بنویسید. کوتاه و روشن باشد بهتر است.",
        "ar": "اكتب العنوان الجديد. الأفضل أن يكون قصيراً وواضحاً.",
        "en": "Write the new title. Short and clear is best.",
    },
    "my_khatms.creator.ask_new_welcome": {
        "fa": "پیام خوش‌آمد جدید را بنویسید.\nبرای پاک‌کردنش، فقط بنویسید «پاک کردن».",
        "ar": "اكتب رسالة الترحيب الجديدة.\nلحذفها فقط اكتب «حذف».",
        "en": "Write the new welcome message.\nTo remove it, just send “clear”.",
    },
    "my_khatms.creator.edit_gone": {
        "fa": "این ختم دیگر در دسترس نیست.", "ar": "هذه الختمة لم تعد متاحة.", "en": "This khatm is no longer available.",
    },
    "my_khatms.creator.edit_cancelled": {
        "fa": "ویرایش لغو شد.", "ar": "تم إلغاء التعديل.", "en": "Edit cancelled.",
    },
    "my_khatms.creator.edit_data_lost": {
        "fa": "اطلاعات ویرایش پاک شده. دوباره از «ختم‌های من» وارد تنظیمات شوید.",
        "ar": "معلومات التعديل ضاعت. ادخل الإعدادات مجدداً من «ختماتي».",
        "en": "The edit details were lost. Enter settings again from “My khatms”.",
    },
    "my_khatms.creator.title_required": {
        "fa": "عنوان نمی‌تواند خالی باشد. یک عنوان کوتاه بنویسید.",
        "ar": "لا يمكن ترك العنوان فارغاً. اكتب عنواناً قصيراً.",
        "en": "The title can't be empty. Please write a short title.",
    },
    "my_khatms.creator.title_saved": {
        "fa": "عنوان ختم ذخیره شد ✅", "ar": "تم حفظ عنوان الختمة ✅", "en": "Khatm title saved ✅",
    },
    "my_khatms.creator.welcome_cleared": {
        "fa": "پیام خوش‌آمد حذف شد ✅", "ar": "تم حذف رسالة الترحيب ✅", "en": "Welcome message removed ✅",
    },
    "my_khatms.creator.welcome_saved": {
        "fa": "پیام خوش‌آمد ذخیره شد ✅", "ar": "تم حفظ رسالة الترحيب ✅", "en": "Welcome message saved ✅",
    },
    "my_khatms.creator.end_at_saved": {
        "fa": "پایان ختم برای {value} تنظیم شد ✅", "ar": "تم ضبط انتهاء الختمة في {value} ✅",
        "en": "Khatm end set for {value} ✅",
    },
    "my_khatms.creator.schedule_date_saved": {
        "fa": "یادآوری برای تاریخ {value} تنظیم شد ✅", "ar": "تم ضبط التذكير لتاريخ {value} ✅",
        "en": "Reminder set for {value} ✅",
    },
    "my_khatms.creator.edit_value_invalid": {
        "fa": "این مقدار قابل‌ذخیره نیست.\nتاریخ پایان مثل این باشد: 2026-10-01 23:00\nتاریخ یادآوری مثل این باشد: 2026-10-01\nعنوان حداکثر ۲۰۰ حرف و پیام خوش‌آمد حداکثر ۵۰۰ حرف باشد.",
        "ar": "لا يمكن حفظ هذه القيمة.\nتاريخ الانتهاء مثل: 2026-10-01 23:00\nتاريخ التذكير مثل: 2026-10-01\nالعنوان حتى ۲۰۰ حرف والترحيب حتى ۵۰۰ حرف.",
        "en": "That value can't be saved.\nEnd date should look like: 2026-10-01 23:00\nReminder date should look like: 2026-10-01\nTitle up to 200 characters, welcome message up to 500.",
    },
    "my_khatms.creator.mode_invalid": {
        "fa": "این فرمت وجود ندارد.", "ar": "هذا الشكل غير موجود.", "en": "That format doesn't exist.",
    },
    "my_khatms.creator.mode_saved": {
        "fa": "فرمت محتوا ذخیره شد ✅", "ar": "تم حفظ شكل المحتوى ✅", "en": "Content format saved ✅",
    },
    "my_khatms.creator.setting_not_available": {
        "fa": "این تنظیم برای این ختم قابل تغییر نیست.", "ar": "لا يمكن تغيير هذا الإعداد لهذه الختمة.",
        "en": "This setting can't be changed for this khatm.",
    },
    "my_khatms.creator.policy_label.pause": {
        "fa": "توقف موقت تعهد", "ar": "الإيقاف المؤقت للالتزام", "en": "Pausing a commitment",
    },
    "my_khatms.creator.policy_label.snooze": {
        "fa": "تعویق یادآوری", "ar": "تأجيل التذكير", "en": "Snoozing the reminder",
    },
    "my_khatms.creator.policy_toggled_on": {
        "fa": "{label} روشن شد ✅", "ar": "تم تفعيل {label} ✅", "en": "{label} turned on ✅",
    },
    "my_khatms.creator.policy_toggled_off": {
        "fa": "{label} خاموش شد.", "ar": "تم إيقاف {label}.", "en": "{label} turned off.",
    },
    "my_khatms.creator.mini_app_https_pending": {
        "fa": "مینی‌اپ هنوز روی آدرس امن آماده نشده. بعد از وصل‌شدن سرور، همین دستور را دوباره بفرستید.",
        "ar": "المصغّر لم يُجهَّز بعد على عنوان آمن. بعد ربط الخادم أرسل نفس الأمر مجدداً.",
        "en": "The Mini App isn't ready on a secure address yet. Send this same command again once the server is connected.",
    },
    "my_khatms.creator.mini_app_needs_khatm": {
        "fa": "این پنل برای کسانی است که یک ختم ساخته‌اند. بعد از ساخت اولین ختمتان، همین دستور را دوباره بفرستید.",
        "ar": "هذه اللوحة لمن أنشأ ختمة. بعد إنشاء ختمتك الأولى، أرسل نفس الأمر مجدداً.",
        "en": "This panel is for people who've created a khatm. Send this same command again after creating your first one.",
    },
    "my_khatms.creator.mini_app_bale_unsupported": {
        "fa": "مینی‌اپ بله هنوز آماده نیست؛ فعلاً ورود ناامن ارائه نمی‌شود.",
        "ar": "المصغّر على بله ليس جاهزاً بعد؛ لا يوجد دخول غير آمن حالياً.",
        "en": "The Bale Mini App isn't ready yet; an insecure login isn't offered.",
    },
    "my_khatms.creator.mini_app_open_prompt": {
        "fa": "پنل خصوصی شما آماده است. با همین دکمه وارد شوید.",
        "ar": "لوحتك الخاصة جاهزة. ادخل من هذا الزر.",
        "en": "Your private panel is ready. Open it with this button.",
    },
    "my_khatms.creator.mini_app_open_button": {
        "fa": "باز کردن مینی‌اپ سازنده", "ar": "فتح مصغّر المنشئ", "en": "Open creator Mini App",
    },
    "my_khatms.creator.members_usage": {
        "fa": "فرمت درست: /khatm_members شناسه‌ی ختم", "ar": "الصيغة الصحيحة: /khatm_members معرّف الختمة",
        "en": "Correct format: /khatm_members khatm id",
    },
    "my_khatms.creator.members_none": {
        "fa": "«{title}» هنوز عضو فعالی ندارد.", "ar": "«{title}» ليس لها أعضاء نشطون بعد.",
        "en": "“{title}” doesn't have any active members yet.",
    },
    "my_khatms.creator.members_header": {
        "fa": "👥 اعضای فعال «{title}» ({count} نفر):", "ar": "👥 الأعضاء النشطون في «{title}» ({count}):",
        "en": "👥 Active members of “{title}” ({count}):",
    },
    "my_khatms.creator.member_no_name": {"fa": "کاربر بدون نام", "ar": "مستخدم بدون اسم", "en": "Unnamed user"},
    "my_khatms.creator.member_progress_quantity": {
        "fa": "پیشرفت {done}/{total}", "ar": "التقدم {done}/{total}", "en": "Progress {done}/{total}",
    },
    "my_khatms.creator.member_progress_portions": {
        "fa": "سهم جاری/تکمیل‌شده {current}/{done}", "ar": "الحصة الحالية/المكتملة {current}/{done}",
        "en": "Current/completed portions {current}/{done}",
    },
    "my_khatms.creator.member_no_portion_yet": {
        "fa": "هنوز سهمی نگرفته", "ar": "لم يأخذ حصة بعد", "en": "Hasn't received a portion yet",
    },
    "my_khatms.creator.member_flag_committed": {"fa": "متعهد", "ar": "ملتزم", "en": "Committed"},
    "my_khatms.creator.member_flag_backup": {"fa": "پشتیبان", "ar": "احتياطي", "en": "Backup"},
    "my_khatms.creator.member_detail_usage": {
        "fa": "فرمت درست: /khatm_member شناسه‌ی ختم شناسه‌ی عضویت",
        "ar": "الصيغة الصحيحة: /khatm_member معرّف الختمة معرّف العضوية",
        "en": "Correct format: /khatm_member khatm id, participation id",
    },
    "my_khatms.creator.member_detail_invalid_ids": {
        "fa": "شناسه‌ی ختم یا عضویت درست نیست.", "ar": "معرّف الختمة أو العضوية غير صحيح.",
        "en": "The khatm id or participation id isn't valid.",
    },
    "my_khatms.creator.member_not_found": {
        "fa": "این عضو پیدا نشد یا این ختم مال شما نیست.", "ar": "لم يتم العثور على هذا العضو أو الختمة ليست لك.",
        "en": "This member wasn't found, or this khatm isn't yours.",
    },
    "my_khatms.creator.member_detail": {
        "fa": (
            "👤 جزئیات «{name}» در «{title}»\n"
            "پیشرفت: {progress}\n{current}\n"
            "دیرکرد در این بازه: {misses}\nیادآوری: {reminder}\n"
            "توقف موقت: {pause}\n"
            "متعهد: {committed}"
        ),
        "ar": (
            "👤 تفاصيل «{name}» في «{title}»\n"
            "التقدم: {progress}\n{current}\n"
            "التأخير في هذه الفترة: {misses}\nالتذكير: {reminder}\n"
            "الإيقاف المؤقت: {pause}\n"
            "ملتزم: {committed}"
        ),
        "en": (
            "👤 Details for “{name}” in “{title}”\n"
            "Progress: {progress}\n{current}\n"
            "Missed in this window: {misses}\nReminder: {reminder}\n"
            "Paused: {pause}\n"
            "Committed: {committed}"
        ),
    },
    "my_khatms.creator.no_portion": {
        "fa": "سهم جاری ندارد", "ar": "لا يملك حصة حالياً", "en": "No current portion",
    },
    "my_khatms.creator.current_portion_quantity": {
        "fa": "سهم جاری: {done}/{total}", "ar": "الحصة الحالية: {done}/{total}", "en": "Current portion: {done}/{total}",
    },
    "my_khatms.creator.current_portion_pages": {
        "fa": "سهم جاری: صفحات {start} تا {end}", "ar": "الحصة الحالية: الصفحات من {start} إلى {end}",
        "en": "Current portion: pages {start} to {end}",
    },
    "my_khatms.creator.pause_none": {"fa": "فعال نیست", "ar": "غير مفعّل", "en": "Not active"},
    "my_khatms.creator.reminder_off": {"fa": "خاموش", "ar": "متوقف", "en": "Off"},
    "my_khatms.creator.yes": {"fa": "بله", "ar": "نعم", "en": "Yes"},
    "my_khatms.creator.no": {"fa": "خیر", "ar": "لا", "en": "No"},
    "my_khatms.creator.attention_usage": {
        "fa": "فرمت درست: /khatm_attention شناسه‌ی ختم", "ar": "الصيغة الصحيحة: /khatm_attention معرّف الختمة",
        "en": "Correct format: /khatm_attention khatm id",
    },
    "my_khatms.creator.attention_empty": {
        "fa": "چیزی برای توجه در «{title}» نیست ✅", "ar": "لا شيء يحتاج انتباهاً في «{title}» ✅",
        "en": "Nothing needs attention in “{title}” ✅",
    },
    "my_khatms.creator.attention_header": {
        "fa": "⚠️ نیاز به توجه در «{title}»", "ar": "⚠️ يحتاج انتباهاً في «{title}»",
        "en": "⚠️ Needs attention in “{title}”",
    },
    "my_khatms.creator.attention_line": {
        "fa": "— {name}: {misses} بار دیرکرد در این بازه", "ar": "— {name}: تأخر {misses} مرة في هذه الفترة",
        "en": "— {name}: missed {misses} time(s) in this window",
    },
    "my_khatms.creator.export_usage": {
        "fa": "فرمت درست: /khatm_export شناسه‌ی ختم", "ar": "الصيغة الصحيحة: /khatm_export معرّف الختمة",
        "en": "Correct format: /khatm_export khatm id",
    },
    "my_khatms.creator.export_empty": {
        "fa": "«{title}» عضو فعالی برای خروجی گرفتن ندارد.", "ar": "«{title}» ليس لها أعضاء نشطون لتصديرهم.",
        "en": "“{title}” has no active members to export.",
    },
    "my_khatms.creator.export_caption": {
        "fa": "گزارش اعضای «{title}»", "ar": "تقرير أعضاء «{title}»", "en": "Member report for “{title}”",
    },
    "my_khatms.creator.export_column.name": {"fa": "نام نمایشی", "ar": "الاسم المعروض", "en": "Display name"},
    "my_khatms.creator.export_column.committed": {"fa": "متعهد", "ar": "ملتزم", "en": "Committed"},
    "my_khatms.creator.export_column.backup": {"fa": "پشتیبان", "ar": "احتياطي", "en": "Backup"},
    "my_khatms.creator.export_column.progress": {"fa": "پیشرفت", "ar": "التقدم", "en": "Progress"},
    "my_khatms.creator.export_column.misses": {"fa": "دیرکرد در بازه", "ar": "التأخير في الفترة", "en": "Missed in window"},
    "my_khatms.creator.stats_usage": {
        "fa": "فرمت درست: /khatm_stats شناسه‌ی ختم", "ar": "الصيغة الصحيحة: /khatm_stats معرّف الختمة",
        "en": "Correct format: /khatm_stats khatm id",
    },
    "my_khatms.creator.phone_not_verified": {
        "fa": "برای ساخت خروجی، اول شماره‌تان را با /verify_phone تأیید کنید.",
        "ar": "لتصدير التقرير، تحقق أولاً من رقمك عبر /verify_phone.",
        "en": "To export this, first verify your number with /verify_phone.",
    },
    "my_khatms.creator.stats_message": {
        "fa": (
            "📈 آمار «{title}»\n"
            "اعضا: {total_members} نفر (فعال {active_members}، تکمیل‌شده {completed_members})\n"
            "اعضای متعهد: {committed_members}\n"
            "سهم‌ها: {completed_portions} از {total_portions} تکمیل شده\n"
            "مشارکت آزاد: {contribution_total:g}\n"
            "دعوت‌ها: {invitations_accepted} از {invitations_issued} پذیرفته شده ({invitation_conversion_percent:g}٪)"
        ),
        "ar": (
            "📈 إحصاءات «{title}»\n"
            "الأعضاء: {total_members} (نشط {active_members}، مكتمل {completed_members})\n"
            "الأعضاء الملتزمون: {committed_members}\n"
            "الحصص: {completed_portions} من {total_portions} مكتملة\n"
            "المشاركة المفتوحة: {contribution_total:g}\n"
            "الدعوات: {invitations_accepted} من {invitations_issued} مقبولة ({invitation_conversion_percent:g}٪)"
        ),
        "en": (
            "📈 Stats for “{title}”\n"
            "Members: {total_members} (active {active_members}, completed {completed_members})\n"
            "Committed members: {committed_members}\n"
            "Portions: {completed_portions} of {total_portions} completed\n"
            "Open contribution: {contribution_total:g}\n"
            "Invitations: {invitations_accepted} of {invitations_issued} accepted ({invitation_conversion_percent:g}%)"
        ),
    },
    "my_khatms.creator.qr_usage": {
        "fa": "فرمت درست: /khatm_qr شناسه‌ی ختم", "ar": "الصيغة الصحيحة: /khatm_qr معرّف الختمة",
        "en": "Correct format: /khatm_qr khatm id",
    },
    "my_khatms.creator.qr_active_only": {
        "fa": "QR دعوت فقط برای ختم فعال ساخته می‌شود.", "ar": "رمز QR للدعوة يُصنع فقط للختمة النشطة.",
        "en": "An invite QR code is only made for an active khatm.",
    },
    "my_khatms.creator.qr_caption": {
        "fa": "QR دعوت «{title}»\n\n{url}", "ar": "رمز دعوة QR لـ«{title}»\n\n{url}",
        "en": "Invite QR code for “{title}”\n\n{url}",
    },
    "my_khatms.creator.qr_caption_with_links": {
        "fa": "QR دعوت «{title}»\n\n🔗 لینک‌های شرکت در ختم:\n\n{invite_lines}",
        "ar": "رمز دعوة QR لـ«{title}»\n\n🔗 روابط المشاركة في الختمة:\n\n{invite_lines}",
        "en": "Invite QR code for “{title}”\n\n🔗 Join links:\n\n{invite_lines}",
    },
    "my_khatms.creator.qr_no_member_bots": {
        "fa": "⚠️ هنوز هیچ ربات عضوی با توکن فعال برای این دسته تنظیم نشده.\nبعد از تنظیم توکن ربات‌ها در پنل مدیریت، دوباره تلاش کنید.",
        "ar": "⚠️ لا يوجد بوت عضو فعّال لهذه الفئة بعد.\nبعد ضبط رموز البوتات في لوحة الإدارة، حاول مرة أخرى.",
        "en": "⚠️ No active member bot is configured for this category yet.\nSet the bot tokens in the admin panel, then try again.",
    },
    "my_khatms.creator.content_mode_usage": {
        "fa": "فرمت درست: /khatm_content_mode شناسه‌ی ختم auto یا photo یا text",
        "ar": "الصيغة الصحيحة: /khatm_content_mode معرّف الختمة auto أو photo أو text",
        "en": "Correct format: /khatm_content_mode khatm id, then auto, photo, or text",
    },
    "my_khatms.creator.content_mode_choice_invalid": {
        "fa": "فرمت باید یکی از این‌ها باشد: auto، photo یا text",
        "ar": "الشكل يجب أن يكون: auto أو photo أو text",
        "en": "The format must be one of: auto, photo, or text",
    },
    "my_khatms.creator.content_mode_label.auto": {"fa": "خودکار", "ar": "تلقائي", "en": "Automatic"},
    "my_khatms.creator.content_mode_label.photo": {"fa": "تصویر", "ar": "صورة", "en": "Photo"},
    "my_khatms.creator.content_mode_label.text": {"fa": "متن", "ar": "نص", "en": "Text"},
    "my_khatms.creator.content_mode_command_saved": {
        "fa": "فرمت محتوای ختم روی «{label}» تنظیم شد ✅", "ar": "تم ضبط شكل محتوى الختمة على «{label}» ✅",
        "en": "Khatm content format set to “{label}” ✅",
    },
    "my_khatms.creator.on_off_usage": {
        "fa": "فرمت درست: {command} شناسه‌ی ختم on یا off",
        "ar": "الصيغة الصحيحة: {command} معرّف الختمة on أو off",
        "en": "Correct format: {command} khatm id, then on or off",
    },
    "my_khatms.creator.pause_command_error": {
        "fa": "این ختم پیدا نشد، مال شما نیست، یا ختم تعهدی فعالی نیست.",
        "ar": "لم يتم العثور على الختمة، أو ليست لك، أو ليست ختمة ملتزمة نشطة.",
        "en": "This khatm wasn't found, isn't yours, or isn't an active committed khatm.",
    },
    "my_khatms.creator.pause_command_saved": {
        "fa": "امکان توقف موقت تعهد در «{title}» {status} شد ✅",
        "ar": "إمكانية الإيقاف المؤقت للالتزام في «{title}» {status} ✅",
        "en": "Pausing a commitment in “{title}” is now {status} ✅",
    },
    "my_khatms.creator.status.on": {"fa": "روشن", "ar": "مفعّلة", "en": "on"},
    "my_khatms.creator.status.off": {"fa": "خاموش", "ar": "متوقفة", "en": "off"},
    "my_khatms.creator.snooze_command_saved": {
        "fa": "امکان تعویق یادآوری در «{title}» {status} شد ✅",
        "ar": "إمكانية تأجيل التذكير في «{title}» {status} ✅",
        "en": "Snoozing reminders in “{title}” is now {status} ✅",
    },
    "my_khatms.creator.end_at_usage": {
        "fa": "فرمت درست: /khatm_end_at شناسه‌ی ختم، بعد تاریخ (مثل 2026-10-01 23:00) یا clear",
        "ar": "الصيغة الصحيحة: /khatm_end_at معرّف الختمة، ثم تاريخ (مثل 2026-10-01 23:00) أو clear",
        "en": "Correct format: /khatm_end_at khatm id, then a date (like 2026-10-01 23:00) or clear",
    },
    "my_khatms.creator.end_at_format_invalid": {
        "fa": "فرمت تاریخ درست نیست. نمونه: /khatm_end_at شناسه 2026-10-01 23:00",
        "ar": "شكل التاريخ غير صحيح. مثال: /khatm_end_at المعرّف 2026-10-01 23:00",
        "en": "The date format isn't right. Example: /khatm_end_at id 2026-10-01 23:00",
    },
    "my_khatms.creator.end_at_command_invalid": {
        "fa": "این ختم پیدا نشد، مال شما نیست، یا تاریخ پایان درست نیست.",
        "ar": "لم يتم العثور على الختمة، أو ليست لك، أو تاريخ الانتهاء غير صحيح.",
        "en": "This khatm wasn't found, isn't yours, or the end date isn't valid.",
    },
    "my_khatms.creator.end_at_command_cleared": {
        "fa": "پایان تاریخی «{title}» حذف شد ✅", "ar": "تم حذف تاريخ انتهاء «{title}» ✅",
        "en": "“{title}”'s end date was removed ✅",
    },
    "my_khatms.creator.end_at_command_set": {
        "fa": "«{title}» در {value} تمام می‌شود ✅", "ar": "«{title}» تنتهي في {value} ✅",
        "en": "“{title}” will end at {value} ✅",
    },
    "my_khatms.creator.schedule_command_usage": {
        "fa": "فرمت: /khatm_schedule شناسه‌ی ختم off یا daily یا weekly:0,2,4 یا every:3 یا date:2026-10-01",
        "ar": "الصيغة: /khatm_schedule معرّف الختمة off أو daily أو weekly:0,2,4 أو every:3 أو date:2026-10-01",
        "en": "Format: /khatm_schedule khatm id, then off, daily, weekly:0,2,4, every:3, or date:2026-10-01",
    },
    "my_khatms.creator.schedule_command_invalid": {
        "fa": "این ختم فعال/آزاد نیست یا فرمت زمان‌بندی درست نیست.",
        "ar": "الختمة ليست نشطة/مفتوحة أو شكل الجدولة غير صحيح.",
        "en": "This khatm isn't active/open, or the schedule format isn't valid.",
    },
    "my_khatms.creator.schedule_command_saved": {
        "fa": "زمان‌بندی مشارکت آزاد «{title}» ذخیره شد ✅", "ar": "تم حفظ جدولة المشاركة المفتوحة لـ«{title}» ✅",
        "en": "Open-participation schedule for “{title}” saved ✅",
    },
    "my_khatms.creator.title_usage": {
        "fa": "فرمت درست: /khatm_edit_title شناسه‌ی ختم، بعد عنوان جدید",
        "ar": "الصيغة الصحيحة: /khatm_edit_title معرّف الختمة، ثم العنوان الجديد",
        "en": "Correct format: /khatm_edit_title khatm id, then the new title",
    },
    "my_khatms.creator.title_command_invalid": {
        "fa": "این ختم پیدا نشد، فعال نیست، مال شما نیست، یا عنوان درست نیست.",
        "ar": "لم يتم العثور على الختمة، أو ليست نشطة، أو ليست لك، أو العنوان غير صحيح.",
        "en": "This khatm wasn't found, isn't active, isn't yours, or the title isn't valid.",
    },
    "my_khatms.creator.title_command_saved": {
        "fa": "عنوان ختم به «{title}» تغییر کرد ✅", "ar": "تغيّر عنوان الختمة إلى «{title}» ✅",
        "en": "Khatm title changed to “{title}” ✅",
    },
    "my_khatms.creator.welcome_usage": {
        "fa": "فرمت درست: /khatm_edit_welcome شناسه‌ی ختم، بعد متن جدید یا clear",
        "ar": "الصيغة الصحيحة: /khatm_edit_welcome معرّف الختمة، ثم النص الجديد أو clear",
        "en": "Correct format: /khatm_edit_welcome khatm id, then the new text or clear",
    },
    "my_khatms.creator.welcome_command_invalid": {
        "fa": "این ختم پیدا نشد، فعال نیست، مال شما نیست، یا متن بیشتر از ۵۰۰ حرف است.",
        "ar": "لم يتم العثور على الختمة، أو ليست نشطة، أو ليست لك، أو النص أطول من ۵۰۰ حرف.",
        "en": "This khatm wasn't found, isn't active, isn't yours, or the text is over 500 characters.",
    },
    "my_khatms.creator.welcome_command_saved": {
        "fa": "پیام خوش‌آمد «{title}» به‌روزرسانی شد ✅", "ar": "تم تحديث رسالة الترحيب في «{title}» ✅",
        "en": "“{title}”'s welcome message was updated ✅",
    },
    "my_khatms.creator.cover_usage": {
        "fa": "فرمت درست caption: /khatm_cover شناسه‌ی ختم", "ar": "شكل caption الصحيح: /khatm_cover معرّف الختمة",
        "en": "Correct caption format: /khatm_cover khatm id",
    },
    "my_khatms.creator.cover_invalid_id": {
        "fa": "شناسه‌ی ختم درست نیست.", "ar": "معرّف الختمة غير صحيح.", "en": "That khatm id isn't valid.",
    },
    "my_khatms.creator.cover_needs_image": {
        "fa": "یک عکس یا فایل تصویر همراه پیامتان بفرستید.",
        "ar": "أرفق صورة أو ملف صورة مع رسالتك.",
        "en": "Attach a photo or image file with your message.",
    },
    "my_khatms.creator.cover_invalid": {
        "fa": "این ختم پیدا نشد، مال شما نیست، یا الان قابل ارسال کاور نیست.",
        "ar": "لم يتم العثور على الختمة، أو ليست لك، أو لا يمكن إرسال غلاف الآن.",
        "en": "This khatm wasn't found, isn't yours, or can't take a cover image right now.",
    },
    "my_khatms.creator.cover_submitted": {
        "fa": "کاور برای بررسی ادمین فرستاده شد ✅", "ar": "أُرسل الغلاف لمراجعة الإدارة ✅",
        "en": "Cover sent for admin review ✅",
    },
    "my_khatms.creator.completion_announcement_on": {
        "fa": "پیام پایان برای همراهان روشن شد ✅", "ar": "تم تفعيل رسالة الانتهاء للأعضاء ✅",
        "en": "The completion message for members is now on ✅",
    },
    "my_khatms.creator.completion_announcement_off": {
        "fa": "پیام پایان برای همراهان خاموش شد.", "ar": "تم إيقاف رسالة الانتهاء للأعضاء.",
        "en": "The completion message for members is now off.",
    },
    "my_khatms.creator.completion_announcement_locked": {
        "fa": "این پیام قبلاً فرستاده شده یا دیگر قابل تغییر نیست.",
        "ar": "هذه الرسالة أُرسلت من قبل أو لم يعد يمكن تغييرها.",
        "en": "This message was already sent, or can no longer be changed.",
    },
    "my_khatms.creator.cancel_ask": {
        "fa": "ختم «{title}» لغو شود؟ این کار فقط قبل از پیوستن اولین نفر ممکن است.\nبازپرداخت به کیف‌پول: {amount:,} تومان",
        "ar": "هل تُلغى ختمة «{title}»؟ هذا ممكن فقط قبل انضمام أول شخص.\nإعادة إلى المحفظة: {amount:,} تومان",
        "en": "Cancel the khatm “{title}”? This is only possible before the first person joins.\nRefund to wallet: {amount:,} Toman",
    },
    "my_khatms.creator.cancel_declined": {
        "fa": "لغو ختم انجام نشد.", "ar": "لم يتم إلغاء الختمة.", "en": "The khatm wasn't cancelled.",
    },
    "my_khatms.creator.cancel_no_access": {
        "fa": "دسترسی ندارید.", "ar": "لا تملك صلاحية.", "en": "You don't have access to this.",
    },
    "my_khatms.creator.cancelled": {
        "fa": "ختم «{title}» لغو شد ✅\nبازپرداخت به کیف‌پول: {amount:,} تومان",
        "ar": "أُلغيت ختمة «{title}» ✅\nأعيد إلى المحفظة: {amount:,} تومان",
        "en": "Khatm “{title}” was cancelled ✅\nRefunded to wallet: {amount:,} Toman",
    },

    # --- Creator Mini App web panel (2026-09-20) ---
    # Scope decision (owner, this session): the web panel IS the content
    # rendered inside the Telegram Mini App — there is no separate
    # standalone "web app". Only the *creator*-facing pages are translated
    # here (creator_base.html, creator_dashboard.html,
    # creator_khatm_detail.html) because creators are regular end users who
    # may not read Persian. The Super-Admin-only pages (dashboard.html,
    # users.html, admins.html, finance.html, etc.) stay Persian, same
    # reasoning as DEC-PY-0075's admin.py decision — admins always work in
    # Persian. See docs/ai/I18N_MIGRATION.md §4 for the checklist.
    "web.label.ACTIVE": {"fa": "فعال", "ar": "نشطة", "en": "Active"},
    "web.label.DRAFT": {"fa": "پیش‌نویس", "ar": "مسودة", "en": "Draft"},
    "web.label.COMPLETED": {"fa": "تمام‌شده", "ar": "مكتملة", "en": "Completed"},
    "web.label.CANCELLED": {"fa": "لغوشده", "ar": "ملغاة", "en": "Cancelled"},
    "web.label.QURAN_PAGE": {"fa": "صفحات قرآن", "ar": "صفحات القرآن", "en": "Quran pages"},
    "web.label.SALAWAT": {"fa": "صلوات", "ar": "صلوات", "en": "Salawat"},
    "web.label.DUA": {"fa": "ادعیه و زیارات", "ar": "الأدعية والزيارات", "en": "Duas and ziyarat"},
    "web.label.ZIYARAT": {"fa": "زیارت", "ar": "زيارة", "en": "Ziyarat"},
    "web.label.LAAN": {"fa": "لعن", "ar": "لعن", "en": "La'an"},
    "web.label.COMMITMENT": {"fa": "تعهدی", "ar": "ملتزمة", "en": "Commitment"},
    "web.label.OPEN": {"fa": "آزاد", "ar": "مفتوحة", "en": "Open"},
    "web.label.MALE": {"fa": "آقا", "ar": "رجل", "en": "Male"},
    "web.label.FEMALE": {"fa": "خانم", "ar": "امرأة", "en": "Female"},

    "web.creator.panel_title": {"fa": "پنل سازنده", "ar": "لوحة المنشئ", "en": "Creator panel"},
    "panel.creator.open_mini_app": {"fa": "🌐 ورود به مینی‌اپ سازنده", "ar": "🌐 فتح تطبيق المنشئ المصغّر", "en": "🌐 Open Creator Mini App"},
    "panel.admin.open_mini_app": {"fa": "🌐 ورود به مینی‌اپ مدیریت", "ar": "🌐 فتح تطبيق الإدارة المصغّر", "en": "🌐 Open Admin Mini App"},
    "web.creator.home_title": {"fa": "ختم‌های من | ختم‌ساز", "ar": "ختماتي | ختم‌ساز", "en": "My Khatms | KhatmSaz"},
    "web.creator.home_aria": {"fa": "خانه پنل سازنده", "ar": "الصفحة الرئيسية للوحة المنشئ", "en": "Creator panel home"},
    "web.creator.secure_logout": {"fa": "خروج امن", "ar": "خروج آمن", "en": "Secure logout"},
    "web.creator.nav_my_khatms": {"fa": "ختم‌های من", "ar": "ختماتي", "en": "My Khatms"},
    "web.creator.nav_home": {"fa": "خانه", "ar": "الرئيسية", "en": "Home"},
    "web.creator.nav_wallet": {"fa": "کیف پول", "ar": "المحفظة", "en": "Wallet"},
    # Dashboard home (redesign 2026-09-29)
    "web.creator.dashboard_subtitle": {"fa": "یک نگاه سریع به همه‌چیز؛ برای مدیریت هر بخش، روی کارت‌ها بزنید.", "ar": "نظرة سريعة على كل شيء؛ اضغط على البطاقات لإدارة كل قسم.", "en": "A quick look at everything — tap a card to manage each area."},
    "web.creator.kpi_active_khatms": {"fa": "ختم فعال", "ar": "ختمة نشطة", "en": "Active khatms"},
    "web.creator.kpi_total_members": {"fa": "کل اعضای فعال", "ar": "إجمالي الأعضاء النشطين", "en": "Total active members"},
    "web.creator.kpi_wallet": {"fa": "موجودی کیف پول", "ar": "رصيد المحفظة", "en": "Wallet balance"},
    "web.creator.kpi_plan": {"fa": "پلن فعلی", "ar": "الباقة الحالية", "en": "Current plan"},
    "web.creator.toman": {"fa": "تومان", "ar": "تومان", "en": "Toman"},
    "web.creator.toman_thousand": {"fa": "هزار تومان", "ar": "ألف تومان", "en": "thousand Toman"},
    "web.creator.quick_actions": {"fa": "دسترسی سریع", "ar": "وصول سريع", "en": "Quick access"},
    "web.creator.action_manage_khatms": {"fa": "مدیریت اعضا، آمار و تنظیمات هر ختم", "ar": "إدارة الأعضاء والإحصاءات وإعدادات كل ختمة", "en": "Manage members, stats and settings"},
    "web.creator.action_topup": {"fa": "افزایش موجودی برای ساخت و خدمات", "ar": "شحن الرصيد للإنشاء والخدمات", "en": "Top up for creating and services"},
    "web.creator.action_create_in_bot": {"fa": "برای ساخت ختم جدید، در بات «➕ ساخت ختم جدید» را بزنید.", "ar": "لإنشاء ختمة جديدة، اضغط «➕ إنشاء ختمة جديدة» في البوت.", "en": "To create a new khatm, tap «➕ Create New Khatm» in the bot."},
    "web.creator.action_create_here": {"fa": "همین‌جا خیلی ساده یک ختم تازه بسازید.", "ar": "أنشئ ختمة جديدة بسهولة من هنا.", "en": "Create a new khatm here in a few simple steps."},
    "web.creator.create_button": {"fa": "➕ ساخت ختم", "ar": "➕ إنشاء ختمة", "en": "➕ Create khatm"},
    "web.creator.create_title": {"fa": "ساخت ختم جدید", "ar": "إنشاء ختمة جديدة", "en": "Create a new khatm"},
    "web.creator.create_subtitle": {"fa": "نوع ختم را انتخاب کنید؛ بقیهٔ مسیر کوتاه و روشن است.", "ar": "اختر نوع الختمة؛ بقية الخطوات قصيرة وواضحة.", "en": "Choose the khatm type; the remaining steps are short and clear."},
    "web.creator.create_back": {"fa": "→ بازگشت به ختم‌های من", "ar": "→ العودة إلى ختماتي", "en": "→ Back to my khatms"},
    "web.creator.create_kind": {"fa": "چه ختمی می‌خواهید؟", "ar": "ما نوع الختمة؟", "en": "What kind of khatm?"},
    "web.creator.kind_quran": {"fa": "قرآن", "ar": "القرآن", "en": "Quran"},
    "web.creator.kind_salawat": {"fa": "صلوات", "ar": "الصلوات", "en": "Salawat"},
    "web.creator.kind_dua": {"fa": "دعا و زیارت", "ar": "الدعاء والزيارة", "en": "Dua & Ziyarat"},
    "web.creator.kind_laan": {"fa": "لعن", "ar": "اللعن", "en": "La'an"},
    "web.creator.create_category": {"fa": "کدام مورد؟", "ar": "أيّ واحد؟", "en": "Which one?"},
    "web.creator.create_category_empty": {"fa": "هنوز مورد فعالی در این بخش ثبت نشده است.", "ar": "لا يوجد عنصر فعّال في هذا القسم بعد.", "en": "No active item has been added to this section yet."},
    "web.creator.create_edition": {"fa": "نسخهٔ قرآن", "ar": "نسخة القرآن", "en": "Quran edition"},
    "web.creator.create_mode": {"fa": "روش همراهی اعضا", "ar": "طريقة مشاركة الأعضاء", "en": "How members participate"},
    "web.creator.create_details": {"fa": "جزئیات کوتاه", "ar": "تفاصيل قصيرة", "en": "A few details"},
    "web.creator.create_optional_title": {"fa": "نام ختم (اختیاری)", "ar": "اسم الختمة (اختياري)", "en": "Khatm name (optional)"},
    "web.creator.create_title_placeholder": {"fa": "اگر خالی بماند، نام مناسب خودکار ساخته می‌شود", "ar": "اتركه فارغاً لإنشاء اسم مناسب تلقائياً", "en": "Leave blank to generate a suitable name"},
    "web.creator.create_amount": {"fa": "تعداد کل یا مقدار تعهد هر عضو", "ar": "العدد الكلي أو مقدار التزام كل عضو", "en": "Total count or each member's pledge"},
    "web.creator.create_visibility": {"fa": "چه کسانی ختم را ببینند؟", "ar": "من يمكنه رؤية الختمة؟", "en": "Who can see the khatm?"},
    "web.creator.visibility_unlisted": {"fa": "فقط کسانی که لینک دارند", "ar": "فقط من لديه الرابط", "en": "Only people with the link"},
    "web.creator.visibility_public": {"fa": "همه؛ در فهرست عمومی", "ar": "الجميع؛ في القائمة العامة", "en": "Everyone; in the public list"},
    "web.creator.visibility_private": {"fa": "خصوصی؛ عضویت با تأیید من", "ar": "خاصة؛ الانضمام بموافقتي", "en": "Private; I approve joins"},
    "web.creator.create_price": {"fa": "هزینهٔ ساخت: {price:,} تومان", "ar": "تكلفة الإنشاء: {price:,} تومان", "en": "Creation cost: {price:,} toman"},
    "web.creator.create_submit": {"fa": "ساخت ختم", "ar": "إنشاء الختمة", "en": "Create khatm"},
    "web.creator.create_role_required": {"fa": "این بخش فقط برای سازنده‌هاست.", "ar": "هذا القسم للمنشئين فقط.", "en": "This section is for creators only."},
    "web.creator.create_error_phone": {"fa": "اول شمارهٔ موبایل خود را در بات تأیید کنید، بعد دوباره برگردید.", "ar": "أكّد رقم جوالك في البوت أولاً ثم عد إلى هنا.", "en": "Verify your mobile number in the bot first, then return here."},
    "web.creator.create_error_plan_cap": {"fa": "به سقف پلن رایگان رسیده‌اید. ختم‌ها و اعضای فعلی شما تغییری نمی‌کنند.", "ar": "بلغت حد الباقة المجانية. لن تتغير ختماتك وأعضاؤك الحاليون.", "en": "You've reached the free-plan cap. Your current khatms and members are unchanged."},
    "web.creator.create_error_wallet": {"fa": "موجودی کیف پول برای ساخت این ختم کافی نیست.", "ar": "رصيد المحفظة غير كافٍ لإنشاء هذه الختمة.", "en": "Your wallet balance isn't enough to create this khatm."},
    "web.creator.create_wallet_link": {"fa": "شارژ کیف پول", "ar": "شحن المحفظة", "en": "Top up wallet"},
    "web.creator.create_error_plan_unavailable": {"fa": "ساخت ختم برای پلن فعلی هنوز فعال نیست.", "ar": "إنشاء الختمة غير مفعّل لهذه الباقة حالياً.", "en": "Khatm creation isn't enabled for the current plan yet."},
    "web.creator.create_error_category": {"fa": "لطفاً یک دعا، زیارت یا لعن فعال انتخاب کنید.", "ar": "اختر دعاءً أو زيارةً أو لعناً مفعّلاً.", "en": "Choose an active dua, ziyarat, or la'an."},
    "web.creator.create_error_amount": {"fa": "لطفاً یک عدد بزرگ‌تر از صفر وارد کنید.", "ar": "أدخل رقماً أكبر من صفر.", "en": "Enter a number greater than zero."},
    "web.creator.create_error_invalid": {"fa": "اطلاعات فرم کامل یا درست نیست؛ دوباره بررسی کنید.", "ar": "بيانات النموذج غير كاملة أو غير صحيحة؛ راجعها مرة أخرى.", "en": "The form is incomplete or invalid; please check it again."},
    "web.creator.recent_khatms": {"fa": "آخرین ختم‌ها", "ar": "أحدث الختمات", "en": "Recent khatms"},
    "web.creator.see_all": {"fa": "دیدن همه", "ar": "عرض الكل", "en": "See all"},
    # Hierarchical khatm list
    "web.creator.khatms_subtitle": {"fa": "ختم‌ها ابتدا بر اساس وضعیت و سپس نوع دسته‌بندی شده‌اند.", "ar": "الختمات مصنّفة حسب الحالة ثم حسب النوع.", "en": "Khatms are grouped first by status, then by type."},
    "web.creator.branch_aria": {"fa": "دسته‌بندی ختم‌ها بر اساس وضعیت", "ar": "تصنيف الختمات حسب الحالة", "en": "Khatms grouped by status"},
    "web.creator.branch_active": {"fa": "فعال", "ar": "نشطة", "en": "Active"},
    "web.creator.branch_completed": {"fa": "تمام‌شده", "ar": "منتهية", "en": "Finished"},
    "web.creator.branch_empty": {"fa": "این بخش هنوز خالی است.", "ar": "هذا القسم فارغ حتى الآن.", "en": "This section is empty for now."},
    "web.creator.members_word": {"fa": "عضو", "ar": "عضو", "en": "members"},
    "web.creator.bucket_quran": {"fa": "قرآن", "ar": "القرآن", "en": "Quran"},
    "web.creator.bucket_salawat": {"fa": "صلوات", "ar": "الصلوات", "en": "Salawat"},
    "web.creator.bucket_dua": {"fa": "دعا و زیارت", "ar": "الأدعية والزيارات", "en": "Dua & Ziyarat"},
    "web.creator.bucket_other": {"fa": "سایر", "ar": "أخرى", "en": "Other"},
    # Wallet page
    "web.creator.wallet_eyebrow": {"fa": "کیف پول و مالی", "ar": "المحفظة والمالية", "en": "Wallet & finance"},
    "web.creator.wallet_subtitle": {"fa": "موجودی خود را ببینید و کیف پول را شارژ کنید.", "ar": "اطّلع على رصيدك واشحن محفظتك.", "en": "See your balance and top up your wallet."},
    "web.creator.wallet_balance": {"fa": "موجودی", "ar": "الرصيد", "en": "Balance"},
    "web.creator.wallet_credit": {"fa": "اعتبار هدیه", "ar": "رصيد هدية", "en": "Reward credit"},
    "web.creator.wallet_topup_title": {"fa": "افزایش موجودی", "ar": "شحن الرصيد", "en": "Top up"},
    "web.creator.wallet_topup_hint": {"fa": "پس از انتخاب مبلغ، به درگاه امن پرداخت هدایت می‌شوید.", "ar": "بعد اختيار المبلغ، سيتم توجيهك إلى بوابة الدفع الآمنة.", "en": "After choosing an amount, you'll be sent to the secure payment gateway."},
    "web.creator.wallet_gateway_off": {"fa": "درگاه پرداخت هنوز فعال نشده است. لطفاً بعداً دوباره تلاش کنید.", "ar": "بوابة الدفع غير مفعّلة بعد. حاول لاحقاً.", "en": "The payment gateway is not active yet. Please try again later."},
    "web.creator.wallet_invoices_title": {"fa": "تاریخچهٔ تراکنش‌ها", "ar": "سجل المعاملات", "en": "Transaction history"},
    "web.creator.wallet_no_invoices": {"fa": "هنوز تراکنشی ثبت نشده است.", "ar": "لا توجد معاملات بعد.", "en": "No transactions yet."},
    "web.creator.wallet_custom_placeholder": {"fa": "مبلغ دلخواه (تومان)", "ar": "مبلغ مخصص (تومان)", "en": "Custom amount (toman)"},
    "web.creator.wallet_custom_button": {"fa": "شارژ", "ar": "شحن", "en": "Top up"},
    # Current plan (read-only) — faithful to backend: no purchase/expiry yet
    "web.creator.plan_section_title": {"fa": "پلن فعلی", "ar": "الباقة الحالية", "en": "Current plan"},
    "web.creator.plan_usage_quran": {"fa": "اعضای قرآن", "ar": "أعضاء القرآن", "en": "Quran members"},
    "web.creator.plan_usage_dev": {"fa": "اعضای صلوات/دعا", "ar": "أعضاء الصلوات/الأدعية", "en": "Salawat/Dua members"},
    "web.creator.plan_cap_note": {"fa": "رسیدن به سقف فقط ساخت ختم جدید را می‌بندد؛ ختم‌های فعلی و عضوگیری آن‌ها ادامه دارند.", "ar": "بلوغ الحد الأقصى يمنع إنشاء ختمة جديدة فقط؛ الختمات الحالية وانضمام الأعضاء إليها مستمرّة.", "en": "Reaching the cap only blocks creating a new khatm; your existing khatms and their joins continue."},
    "web.creator.plan_paid_no_limit": {"fa": "پلن‌های پولی در نسخهٔ فعلی محدودیت عضو ندارند.", "ar": "الباقات المدفوعة لا تحدّ عدد الأعضاء في النسخة الحالية.", "en": "Paid plans have no member limit in the current version."},
    "web.creator.plan_free_name": {"fa": "رایگان", "ar": "مجانية", "en": "Free"},
    "web.creator.plan_pro_name": {"fa": "پرو", "ar": "احترافية", "en": "Pro"},
    "web.creator.plan_current_badge": {"fa": "فعلی", "ar": "الحالية", "en": "current"},
    "web.creator.plan_free_quran": {"fa": "سقف اعضای قرآن: {n}", "ar": "حد أعضاء القرآن: {n}", "en": "Quran member cap: {n}"},
    "web.creator.plan_free_dev": {"fa": "سقف اعضای صلوات/دعا: {n}", "ar": "حد أعضاء الصلوات/الأدعية: {n}", "en": "Salawat/Dua member cap: {n}"},
    "web.creator.plan_pro_unlimited": {"fa": "بدون محدودیت تعداد عضو", "ar": "بدون حد لعدد الأعضاء", "en": "No member limit"},
    "web.creator.plan_buy_pro": {"fa": "خرید پلن پرو · {price:,} تومان", "ar": "شراء باقة برو · {price:,} تومان", "en": "Buy Pro · {price:,} toman"},
    "web.creator.plan_not_enabled": {"fa": "خرید پلن پرو هنوز فعال نشده", "ar": "شراء باقة برو غير مفعّل بعد", "en": "Pro purchasing isn't enabled yet"},
    "web.creator.plan_unlimited": {"fa": "نامحدود", "ar": "غير محدود", "en": "Unlimited"},
    "web.creator.plan_pro_threshold": {
        "fa": "با موجودی کیف پول حداقل {price:,} تومان، خودکار فعال می‌شود.",
        "ar": "يُفعّل تلقائيًا عند بلوغ رصيد المحفظة {price:,} تومان.",
        "en": "Activates automatically when wallet funds reach {price:,} toman.",
    },
    "report.today_pick": {
        "fa": "امروز سهم کدام ختم را می‌خواهید زودتر بخوانید؟",
        "ar": "أي ختمة تريد أن تقرأ حصتها مبكرًا اليوم؟",
        "en": "Which khatm would you like to read early today?",
    },
    "report.today_already_delivered": {
        "fa": "سهم امروز این ختم قبلاً برایتان فرستاده شده است.",
        "ar": "أُرسلت إليك حصة هذه الختمة اليوم بالفعل.",
        "en": "Today's share for this khatm has already been sent.",
    },
    "report.today_already_completed": {
        "fa": "سهم امروز این ختم را انجام داده‌اید؛ سهم بعدی برای روز بعد است.",
        "ar": "أنجزت حصة هذه الختمة اليوم؛ الحصة التالية لليوم القادم.",
        "en": "You completed today's share; the next share is for the next day.",
    },
    "report.content_unavailable": {
        "fa": "محتوای این ختم هنوز در دسترس نیست؛ چیزی به‌عنوان سهم امروز ثبت نشد. لطفاً کمی بعد دوباره امتحان کنید.",
        "ar": "محتوى هذه الختمة غير متاح الآن؛ لم تُسجّل حصة اليوم. يرجى المحاولة لاحقًا.",
        "en": "This khatm's content is not available yet; today's share was not recorded. Please try again later.",
    },
    "report.today_open": {
        "fa": "🌱 سهم امروزتان در «{title}» آماده است؛ بعد از انجام، مقدارش را ثبت کنید.",
        "ar": "🌱 حصة اليوم من «{title}» جاهزة؛ بعد إنجازها سجّل الكمية.",
        "en": "🌱 Today's share in “{title}” is ready; log the amount after completing it.",
    },
    "report.today_do_share": {
        "fa": "پس از قرائت، دکمهٔ زیر را بزنید 🌱",
        "ar": "بعد القراءة، اضغط الزر أدناه 🌱",
        "en": "After reading, tap the button below 🌱",
    },
    "web.creator.plan_purchase_success": {"fa": "پلن پرو با موفقیت فعال شد ✅ این پلن فعلاً دائمی است.", "ar": "تم تفعيل باقة برو بنجاح ✅ هذه الباقة دائمة حالياً.", "en": "Pro was activated successfully ✅ This plan is currently permanent."},
    "web.creator.plan_already_pro": {"fa": "پلن شما از قبل پرو است و دوباره هزینه‌ای کم نشد.", "ar": "باقتك برو بالفعل ولم تُخصم أي تكلفة مرة أخرى.", "en": "You're already on Pro, so you weren't charged again."},
    "web.creator.plan_purchase_insufficient": {"fa": "موجودی برای خرید پرو کافی نیست.", "ar": "الرصيد غير كافٍ لشراء برو.", "en": "Your balance isn't enough to buy Pro."},
    "web.creator.plan_purchase_unavailable": {"fa": "خرید پرو هنوز توسط مدیر فعال و قیمت‌گذاری نشده است.", "ar": "شراء برو لم يُفعّل أو يُسعّر من الإدارة بعد.", "en": "Pro purchasing hasn't been enabled and priced by an admin yet."},
    "web.creator.eyebrow_private_report": {"fa": "گزارش خصوصی سازنده", "ar": "تقرير خاص بالمنشئ", "en": "Private creator report"},
    "web.creator.greeting": {"fa": "سلام {name}", "ar": "مرحباً {name}", "en": "Hello {name}"},
    "web.creator.default_name": {"fa": "دوست عزیز", "ar": "صديقنا العزيز", "en": "dear friend"},
    "web.creator.pick_khatm_hint": {
        "fa": "برای دیدن اعضا و پیشرفت، یکی از ختم‌ها را انتخاب کنید.",
        "ar": "لعرض الأعضاء والتقدم، اختر إحدى الختمات.",
        "en": "To see members and progress, choose one of your khatms.",
    },
    "web.creator.active_members_suffix": {
        "fa": "{count} عضو فعال · {template} · {mode}", "ar": "{count} عضو نشط · {template} · {mode}",
        "en": "{count} active members · {template} · {mode}",
    },
    "web.creator.no_khatms_yet": {
        "fa": "هنوز ختمی نساخته‌اید.", "ar": "لم تُنشئ أي ختمة بعد.", "en": "You haven't created any khatm yet.",
    },
    "web.creator.pagination_aria": {
        "fa": "صفحه‌بندی ختم‌های سازنده", "ar": "ترقيم صفحات ختمات المنشئ", "en": "Creator khatm list pagination",
    },
    "web.creator.prev_page": {"fa": "صفحه قبل", "ar": "الصفحة السابقة", "en": "Previous page"},
    "web.creator.next_page": {"fa": "صفحه بعد", "ar": "الصفحة التالية", "en": "Next page"},
    "web.creator.page_label": {"fa": "صفحه {page}", "ar": "صفحة {page}", "en": "Page {page}"},

    "web.creator.back_to_my_khatms": {
        "fa": "→ بازگشت به ختم‌های من", "ar": "→ العودة إلى ختماتي", "en": "→ Back to My Khatms",
    },
    "web.creator.eyebrow_member_report": {
        "fa": "گزارش خصوصی اعضا", "ar": "تقرير خاص بالأعضاء", "en": "Private member report",
    },
    "web.creator.member_report_notice": {
        "fa": "این اطلاعات فقط برای مدیریت همین ختم نمایش داده می‌شود و نباید برای دیگران ارسال شود.",
        "ar": "تُعرض هذه المعلومات فقط لإدارة هذه الختمة ويجب ألا تُرسل للآخرين.",
        "en": "This information is shown only for managing this khatm and shouldn't be sent to anyone else.",
    },
    "web.creator.metric_active_members": {"fa": "عضو فعال", "ar": "عضو نشط", "en": "Active members"},
    "web.creator.metric_completed_portions": {"fa": "سهم تکمیل", "ar": "الحصص المكتملة", "en": "Portions completed"},
    "web.creator.metric_open_contribution": {"fa": "مشارکت آزاد", "ar": "المشاركة المفتوحة", "en": "Open contribution"},
    "web.creator.search_placeholder": {
        "fa": "نام، شماره موبایل، استان یا شهر", "ar": "الاسم، رقم الجوال، المحافظة أو المدينة",
        "en": "Name, phone number, province, or city",
    },
    "web.creator.search_button": {"fa": "جست‌وجو", "ar": "بحث", "en": "Search"},
    "web.creator.download_full_xlsx": {
        "fa": "⬇️ دریافت اکسل کامل اعضا", "ar": "⬇️ تنزيل ملف إكسل الكامل للأعضاء", "en": "⬇️ Download full member Excel file",
    },
    "web.creator.no_name": {"fa": "بدون نام", "ar": "بدون اسم", "en": "No name"},
    "web.creator.field_mobile": {"fa": "موبایل", "ar": "الجوال", "en": "Mobile"},
    "web.creator.not_registered": {"fa": "ثبت نشده", "ar": "غير مسجَّل", "en": "Not registered"},
    "web.creator.field_province_city": {"fa": "استان / شهر", "ar": "المحافظة / المدينة", "en": "Province / City"},
    "web.creator.field_gender": {"fa": "جنسیت", "ar": "الجنس", "en": "Gender"},
    "web.creator.field_membership_type": {"fa": "نوع عضویت", "ar": "نوع العضوية", "en": "Membership type"},
    "web.creator.open_companion": {"fa": "آزاد / همراه", "ar": "مفتوحة / مرافق", "en": "Open / companion"},
    "web.creator.backup_reader_suffix": {"fa": " · یار ذخیره", "ar": " · احتياطي", "en": " · backup reader"},
    "web.creator.field_completed_portion": {"fa": "سهم تکمیل‌شده", "ar": "الحصة المكتملة", "en": "Completed portion"},
    "web.creator.field_recorded_misses": {"fa": "پیگیری ثبت‌شده", "ar": "المتابعات المسجَّلة", "en": "Recorded follow-ups"},
    "web.creator.field_contribution": {"fa": "مشارکت", "ar": "المشاركة", "en": "Contribution"},
    "web.creator.field_surplus": {"fa": "مازاد", "ar": "الفائض", "en": "Surplus"},
    "web.creator.no_member_found": {
        "fa": "عضوی با این جست‌وجو پیدا نشد.", "ar": "لم يتم العثور على عضو بهذا البحث.", "en": "No member found for this search.",
    },
    "web.creator.member_pagination_aria": {"fa": "صفحه‌بندی اعضا", "ar": "ترقيم صفحات الأعضاء", "en": "Member list pagination"},
    "web.creator.khatm_not_found": {
        "fa": "این ختم در پنل شما وجود ندارد.", "ar": "هذه الختمة غير موجودة في لوحتك.", "en": "This khatm doesn't exist in your panel.",
    },
    "web.creator.invalid_security_request": {"fa": "درخواست امنیتی نامعتبر است.", "ar": "طلب الأمان غير صالح.", "en": "Invalid security request."},
    "web.creator.settings_title": {"fa": "تنظیمات این ختم", "ar": "إعدادات هذا الختم", "en": "Khatm settings"},
    "web.creator.settings_hint": {"fa": "نام، پیام خوش‌آمد و رفتار یادآوری را همین‌جا تغییر دهید.", "ar": "غيّر الاسم ورسالة الترحيب وسلوك التذكير هنا.", "en": "Change the name, welcome message, and reminder behavior here."},
    "web.creator.settings_khatm_name": {"fa": "نام ختم", "ar": "اسم الختم", "en": "Khatm name"},
    "web.creator.settings_welcome": {"fa": "پیام خوش‌آمد", "ar": "رسالة الترحيب", "en": "Welcome message"},
    "web.creator.settings_welcome_hint": {"fa": "این پیام بعد از عضویت به عضو نشان داده می‌شود.", "ar": "تظهر هذه الرسالة للعضو بعد الانضمام.", "en": "Members see this message after joining."},
    "web.creator.settings_allow_pause": {"fa": "عضو بتواند تعهدش را موقتاً متوقف کند", "ar": "السماح للعضو بإيقاف التزامه مؤقتاً", "en": "Allow members to pause their commitment"},
    "web.creator.settings_allow_snooze": {"fa": "عضو بتواند یادآوری را عقب بیندازد", "ar": "السماح للعضو بتأجيل التذكير", "en": "Allow members to snooze reminders"},
    "web.creator.settings_allow_skip_today": {"fa": "عضو بتواند سهم امروز را رد کند", "ar": "السماح للعضو بتجاوز حصة اليوم", "en": "Allow members to skip today's portion"},
    "web.creator.settings_miss_threshold": {"fa": "بعد از چند بار پیگیری شود؟", "ar": "بعد كم مرة تتم المتابعة؟", "en": "Follow up after how many misses?"},
    "web.creator.settings_miss_window": {"fa": "در بازهٔ چند روزه؟", "ar": "خلال كم يوماً؟", "en": "Within how many days?"},
    "web.creator.settings_schedule": {"fa": "برنامهٔ دریافت سهم", "ar": "جدول استلام الحصة", "en": "Portion schedule"},
    "web.creator.schedule_off": {"fa": "بدون برنامهٔ خودکار", "ar": "بدون جدول تلقائي", "en": "No automatic schedule"},
    "web.creator.schedule_daily": {"fa": "هر روز", "ar": "كل يوم", "en": "Every day"},
    "web.creator.schedule_workdays": {"fa": "روزهای کاری", "ar": "أيام العمل", "en": "Workdays"},
    "web.creator.schedule_weekend": {"fa": "آخر هفته", "ar": "نهاية الأسبوع", "en": "Weekend"},
    "web.creator.schedule_every_three": {"fa": "هر سه روز", "ar": "كل ثلاثة أيام", "en": "Every three days"},
    "web.creator.settings_completion_announcement": {"fa": "پس از پایان، پیام تکمیل ختم برای اعضا فرستاده شود", "ar": "إرسال رسالة إتمام الختم للأعضاء بعد انتهائه", "en": "Send members a completion message when the khatm finishes"},
    "web.creator.settings_save": {"fa": "ذخیرهٔ تنظیمات", "ar": "حفظ الإعدادات", "en": "Save settings"},
    "web.creator.settings_saved": {"fa": "تنظیمات ختم ذخیره شد ✅", "ar": "تم حفظ إعدادات الختم ✅", "en": "Khatm settings saved ✅"},
    "web.creator.settings_active_only": {"fa": "تنظیمات فقط تا زمانی که ختم فعال است قابل تغییرند.", "ar": "يمكن تغيير الإعدادات فقط عندما يكون الختم نشطاً.", "en": "Settings can only be changed while the khatm is active."},
    "web.creator.settings_invalid": {"fa": "یکی از تنظیمات معتبر نیست؛ مقدارها را بررسی کنید.", "ar": "أحد الإعدادات غير صالح؛ راجع القيم.", "en": "One of the settings is invalid; please check the values."},
    "web.creator.login_only_mini_app": {
        "fa": "ورود با لینک معمولی غیرفعال است.", "ar": "تسجيل الدخول برابط عادي معطّل.", "en": "Logging in with a regular link is disabled.",
    },
    # --- create_khatm.py: optional creator-authored recitation text
    # (2026-09-21, owner request: "کسی که داره لعن می‌سازه بتونه متن
    # لعنش رو بنویسه تا برای اعضا بره") ---
    "create_khatm.ask_recitation_text": {
        "fa": "متن دقیق این لعن رو بفرستید تا بعد از هر بار مشارکت، برای اعضا هم ارسال بشه "
        "(اختیاری، حداکثر ۳۵۰۰ کاراکتر). اگه نمی‌خواید، دکمهٔ رد کردن رو بزنید.",
        "ar": "أرسل النص الدقيق لهذا اللعن ليُرسل للأعضاء بعد كل مشاركة "
        "(اختياري، حتى ۳۵۰۰ حرف). إذا لا تريد، اضغط زر التخطي.",
        "en": "Send the exact text of this la'an so it's delivered to "
        "members after each contribution (optional, up to 3500 characters). Tap Skip if you don't want to.",
    },
    "create_khatm.recitation_text_too_long": {
        "fa": "این متن خیلی بلنده؛ حداکثر ۳۵۰۰ کاراکتر بفرستید.",
        "ar": "هذا النص طويل جداً؛ أرسل حتى ۳۵۰۰ حرف كحد أقصى.",
        "en": "This text is too long; please send up to 3500 characters.",
    },
    "create_khatm.confirm.recitation_text_set": {
        "fa": "\nمتن اختصاصی برای اعضا: تنظیم شده ✅", "ar": "\nنص مخصص للأعضاء: تم ضبطه ✅",
        "en": "\nCustom text for members: set ✅",
    },

    # --- suggestions.py: user feedback/bug-report inbox to admins
    # (2026-09-21, owner request) ---
    "suggestions.button.open": {
        "fa": "💡 پیشنهاد یا گزارش مشکل", "ar": "💡 اقتراح أو الإبلاغ عن مشكلة", "en": "💡 Suggest or report a problem",
    },
    "suggestions.ask_text": {
        "fa": "چه پیشنهادی دارید، یا چه چیزی خرابه؟ همین‌جا بنویسید (حداکثر ۱۰۰۰ کاراکتر)؛ مستقیم برای مدیریت ارسال می‌شه.",
        "ar": "ما اقتراحك، أو ما الذي لا يعمل؟ اكتبه هنا (حتى ۱۰۰۰ حرف)؛ يُرسل مباشرة للإدارة.",
        "en": "What's your suggestion, or what's broken? Write it here (up to 1000 characters); it goes straight to the admin team.",
    },
    "suggestions.text_required": {
        "fa": "لطفاً یک متن بنویسید.", "ar": "يرجى كتابة نص.", "en": "Please write some text.",
    },
    "suggestions.text_too_long": {
        "fa": "لطفاً حداکثر ۱۰۰۰ کاراکتر بنویسید.", "ar": "يرجى كتابة حتى ۱۰۰۰ حرف كحد أقصى.",
        "en": "Please keep it to 1000 characters or fewer.",
    },
    "suggestions.submitted_to_creator": {
        "fa": "پیام شما به سازندهٔ ختم ارسال شد ✅ به‌زودی پاسخ می‌دهند.",
        "ar": "تم إرسال رسالتك إلى منشئ الختمة ✅ سيردّون قريباً.",
        "en": "Your message was sent to the khatm creator ✅ They'll reply soon.",
    },
    "suggestions.submitted": {
        "fa": "پیشنهادتون ثبت و برای مدیریت ارسال شد ✅ ممنون که وقت گذاشتید.",
        "ar": "تم تسجيل اقتراحك وإرساله للإدارة ✅ شكراً لوقتك.",
        "en": "Your suggestion was recorded and sent to the admin team ✅ Thanks for taking the time.",
    },
    "suggestions.admin_notice": {
        "fa": "💡 پیشنهاد/گزارش جدید از {name}:\n\n{text}",
        "ar": "💡 اقتراح/بلاغ جديد من {name}:\n\n{text}",
        "en": "💡 New suggestion/report from {name}:\n\n{text}",
    },
    "suggestions.default_name": {"fa": "یک کاربر", "ar": "أحد المستخدمين", "en": "a user"},

    "web.creator.login_mini_app_only_notice": {
        "fa": "این بخش فقط به‌صورت مینی‌اپ باز می‌شود. داخل بات دستور /creator_app را بفرستید و دکمهٔ «باز کردن مینی‌اپ سازنده» را لمس کنید.",
        "ar": "يُفتح هذا القسم فقط كتطبيق مصغّر. أرسل الأمر /creator_app داخل البوت واضغط زر «فتح تطبيق المنشئ المصغّر».",
        "en": "This section only opens as a Mini App. Send /creator_app in the bot and tap “Open creator Mini App”.",
    },

    # start.py — join-flow error / status messages
    "join.error.invalid_link": {
        "fa": "این لینک دعوت معتبر نیست یا اشتباه کپی شده. از سازندهٔ ختم بخواهید یک لینک تازه برایتان بفرستد.",
        "ar": "رابط الدعوة هذا غير صالح أو تمّت نسخه بشكل خاطئ. اطلب من منشئ الختمة إرسال رابط جديد.",
        "en": "This invitation link is invalid or was copied incorrectly. Ask the khatm creator to send you a fresh link.",
    },
    "join.error.expired_link": {
        "fa": "این لینک دعوت منقضی شده و دیگر کار نمی‌کند. از سازندهٔ ختم بخواهید یک لینک جدید برایتان بفرستد.",
        "ar": "انتهت صلاحية رابط الدعوة هذا ولم يعد يعمل. اطلب من منشئ الختمة إرسال رابط جديد.",
        "en": "This invitation link has expired and no longer works. Ask the khatm creator to send you a new link.",
    },
    "join.error.khatm_gone": {
        "fa": "این ختم حذف شده یا سازنده‌اش آن را غیرفعال کرده؛ دیگر نمی‌توانید به آن بپیوندید.",
        "ar": "تمّ حذف هذه الختمة أو أوقف منشئها تشغيلها؛ لا يمكنك الانضمام إليها بعد الآن.",
        "en": "This khatm has been removed or deactivated by its creator; you can no longer join it.",
    },
    "join.error.already_member": {
        "fa": "شما از قبل عضو این ختم هستید.",
        "ar": "أنت بالفعل عضو في هذه الختمة.",
        "en": "You are already a member of this khatm.",
    },
    "join.error.khatm_ended": {
        "fa": "این ختم به پایان رسیده یا دیگر فعال نیست.",
        "ar": "انتهت هذه الختمة أو لم تعد نشطة.",
        "en": "This khatm has ended or is no longer active.",
    },
    "join.cancelled": {
        "fa": "عضویت لغو شد.",
        "ar": "تمّ إلغاء الانضمام.",
        "en": "Joining was cancelled.",
    },
    "join.commitment_cancelled": {
        "fa": "عضویت تعهدی لغو شد.",
        "ar": "تمّ إلغاء الانضمام الملتزم.",
        "en": "Committed membership was cancelled.",
    },
    "join.commitment_expired": {
        "fa": "درخواست عضویت منقضی شده؛ دوباره لینک دعوت را باز کنید.",
        "ar": "انتهت صلاحية طلب الانضمام؛ افتح رابط الدعوة مرةً أخرى.",
        "en": "The join request has expired; please open the invitation link again.",
    },
    "join.commitment_consent": {
        "fa": (
            "⚠️ <b>این یک تعهد است، نه فقط یک دکمه.</b>\n\n"
            "با پذیرش، شرعاً و اخلاقاً متعهد می‌شوید سهمی که برمی‌دارید را <b>حتماً</b> و سر وقت بخوانید.\n"
            "اگر انجام ندهید، ختمِ جمعی و ثوابِ بقیهٔ شرکت‌کننده‌ها را ناقص و خراب می‌کنید و "
            "این تعهد بر عهدهٔ شما یک <b>دِین</b> است که باید ادا شود.\n\n"
            "اگر مطمئن نیستید می‌توانید انجامش دهید، لطفاً تعهد ندهید.\n\n"
            "تعهد را با آگاهی می‌پذیرید؟"
        ),
        "ar": (
            "⚠️ <b>هذا التزام، وليس مجرّد زر.</b>\n\n"
            "بالقبول، تتعهّد شرعاً وأخلاقياً بأن تقرأ حصتك <b>حتماً</b> وفي وقتها.\n"
            "إن لم تفعل، فإنك تُفسد الختمة الجماعية وثواب بقية المشاركين، ويصبح هذا الالتزام "
            "<b>ديناً</b> في ذمّتك يجب أداؤه.\n\n"
            "إن لم تكن واثقاً من قدرتك، فالرجاء عدم الالتزام.\n\n"
            "هل تقبل الالتزام عن وعي؟"
        ),
        "en": (
            "⚠️ <b>This is a commitment, not just a button.</b>\n\n"
            "By accepting, you pledge — religiously and morally — to read your portion <b>without fail</b> and on time.\n"
            "If you don't, you spoil the collective khatm and everyone else's reward, and this commitment becomes "
            "a <b>debt</b> upon you that must be fulfilled.\n\n"
            "If you're not sure you can, please don't commit.\n\n"
            "Do you knowingly accept the commitment?"
        ),
    },
    "join.private_request_sent": {
        "fa": "این ختم خصوصیه — درخواستتون برای سازندهٔ «{title}» ارسال شد. بعد از تایید بهتون خبر می‌دیم 🌱",
        "ar": "هذه ختمة خاصة — تمّ إرسال طلبك إلى منشئ ختمة «{title}». سنُبلغك بعد الموافقة 🌱",
        "en": "This khatm is private — your request was sent to the creator of «{title}». We'll notify you once it's approved 🌱",
    },
    "join.cover_caption": {
        "fa": "کاور ختم",
        "ar": "غلاف الختمة",
        "en": "Khatm cover",
    },
    "menu.public_khatms": {
        "fa": "🌍 ختم‌های عمومی",
        "ar": "🌍 الختمات العامة",
        "en": "🌍 Public Khatms",
    },
    "menu.support": {
        "fa": "📞 ارتباط با پشتیبانی",
        "ar": "📞 الدعم الفني",
        "en": "📞 Contact Support",
    },
    "web.creator.plan_total_audience": {"fa": "مجموع مخاطبان شما (همهٔ ختم‌ها)", "ar": "إجمالي جمهورك (كل الختمات)", "en": "Your total audience (all khatms)"},
    "web.creator.plan_ads_on": {"fa": "⚠️ در پلن فعلی ممکن است برای مخاطبان شما پیام تبلیغاتی خدمتگزاران ارسال شود. برای حذف تبلیغ، پلن پرو را تهیه کنید.", "ar": "⚠️ في باقتك الحالية قد تُرسَل رسائل ترويجية لجمهورك. للإزالة، اقتنِ الباقة الاحترافية.", "en": "⚠️ On your current plan, promo messages may be sent to your audience. Get Pro to remove ads."},
    "web.creator.plan_ads_off": {"fa": "✅ در پلن فعلی هیچ تبلیغی برای مخاطبان شما ارسال نمی‌شود.", "ar": "✅ لا تُرسَل أي إعلانات لجمهورك في باقتك الحالية.", "en": "✅ No ads are sent to your audience on your current plan."},
    "web.creator.plan_basic_name": {"fa": "پلن پایه", "ar": "الباقة الأساسية", "en": "Basic"},
    "web.creator.plan_free_desc": {"fa": "تا سقف مشخصِ مخاطب، رایگان و بدون تبلیغ.", "ar": "مجاني وبدون إعلانات حتى حدّ جمهور معيّن.", "en": "Free and ad-free up to a set audience cap."},
    "web.creator.plan_basic_desc": {"fa": "بعد از عبور از سقف رایگان؛ ختم‌ها ادامه دارند اما تبلیغ خدمتگزاران فعال می‌شود.", "ar": "بعد تجاوز الحد المجاني؛ تستمر الختمات لكن تُفعَّل الإعلانات.", "en": "After the free cap; khatms continue but خدمتگزاران ads turn on."},
    "web.creator.plan_pro_desc": {"fa": "بدون تبلیغ؛ با خرید بستهٔ نفرات و امکان پیام تبلیغاتی به مخاطبان.", "ar": "بدون إعلانات؛ بشراء باقة أعضاء وإمكانية مراسلة الجمهور.", "en": "No ads; buy member blocks and message your audience."},
    "plan.autoupgrade_basic_notice": {
        "fa": "🌱 تعداد کل مخاطبان ختم‌های شما از سقف پلن رایگان گذشت، پس وارد «پلن پایه» شدید.\n\nدر پلن پایه، ممکن است از طرف خدمتگزاران برای مخاطبان شما پیام تبلیغاتی ارسال شود. اگر می‌خواهید تبلیغی ارسال نشود، کیف پول را شارژ و «پلن پرو» را تهیه کنید.",
        "ar": "🌱 تجاوز إجمالي جمهور ختماتك سقف الباقة المجانية، لذا انتقلت إلى «الباقة الأساسية».\n\nفي الباقة الأساسية قد تُرسَل رسائل ترويجية لجمهورك من الخدمتغزاران. إن أردت إيقافها، اشحن محفظتك واقتنِ «الباقة الاحترافية».",
        "en": "🌱 Your total audience passed the free-plan cap, so you moved to the Basic plan.\n\nOn Basic, promotional messages may be sent to your audience. To stop ads, top up your wallet and get the Pro plan.",
    },
    "menu.contact_creator": {
        "fa": "✉️ ارتباط با سازندهٔ ختم",
        "ar": "✉️ التواصل مع منشئ الختمة",
        "en": "✉️ Contact the khatm creator",
    },
    "menu.about_us": {
        "fa": "ℹ️ درباره ما",
        "ar": "ℹ️ من نحن",
        "en": "ℹ️ About Us",
    },
    "about_us.text": {
        "fa": (
            "🌸 <b>تیم خدمتگزاران تک</b>\n\n"
            "سامانه ختم‌ساز جهت تسهیل و سازماندهی ختم‌های جمعی قرآن، صلوات، ادعیه و زیارات "
            "به نیت سلامتی و فرج امام عصر عجل‌الله‌تعالی‌فرجه‌الشریف طراحی شده است 🌱\n\n"
            "📬 ارتباط و پشتیبانی: @khedmatgozaran_khadem"
        ),
        "ar": (
            "🌸 <b>فريق خدمة تك</b>\n\n"
            "منصة ختم‌ساز لتنظيم الختمات الجماعية للقرآن والصلوات والأدعية والزيارات "
            "بنية فرج وسلامة إمام العصر عجل الله تعالى فرجه الشريف 🌱\n\n"
            "📬 الدعم والتواصل: @khedmatgozaran_khadem"
        ),
        "en": (
            "🌸 <b>Khedmatgozaran Tech Team</b>\n\n"
            "KhatmSaz platform for organizing collective recitations of Quran, Salawat, Duas, and Ziyarats "
            "dedicated to Imam Mahdi (AJ) 🌱\n\n"
            "📬 Contact & Support: @khedmatgozaran_khadem"
        ),
    },
    "menu.custom_khatm": {
        "fa": "✨ ساخت ختم اختصاصی",
        "ar": "✨ إنشاء ختمة خاصة",
        "en": "✨ Request a custom khatm",
    },
    "custom_khatm.contact": {
        "fa": "برای ساخت ختم اختصاصی، شمارهٔ مدیریت را ذخیره کنید و در تلگرام یا بله به همین شماره پیام بدهید:\n\n📱 {phone}",
        "ar": "لإنشاء ختمة خاصة، احفظ رقم الإدارة وأرسل رسالة إليه عبر تلغرام أو بله:\n\n📱 {phone}",
        "en": "To request a custom khatm, save the admin number and message it on Telegram or Bale:\n\n📱 {phone}",
    },
    "custom_khatm.unavailable": {
        "fa": "شمارهٔ ساخت ختم اختصاصی هنوز توسط مدیریت ثبت نشده است.",
        "ar": "لم تسجل الإدارة رقم طلب الختمة الخاصة بعد.",
        "en": "The admin contact number for custom khatms has not been configured yet.",
    },
    "contact_creator.none": {
        "fa": "شما هنوز در هیچ ختمی عضو نیستید. بعد از پیوستن به یک ختم، می‌تونید همین‌جا با سازنده‌اش در ارتباط باشید.",
        "ar": "لست عضواً في أي ختمة بعد. بعد الانضمام إلى ختمة يمكنك التواصل مع منشئها من هنا.",
        "en": "You haven't joined any khatm yet. Once you join one, you can contact its creator here.",
    },
    "contact_creator.pick": {
        "fa": "پیام شما به کدام سازنده برسد؟ یکی را انتخاب کنید:",
        "ar": "إلى أي منشئ تريد إرسال رسالتك؟ اختر واحداً:",
        "en": "Which creator should get your message? Pick one:",
    },
    "contact_creator.ask_text": {
        "fa": "پیام‌تان را برای سازندهٔ «{name}» بنویسید:",
        "ar": "اكتب رسالتك لمنشئ «{name}»:",
        "en": "Write your message for the creator of “{name}”:",
    },
    "menu.creator_request": {
        "fa": "🌱 درخواست سازنده‌شدن",
        "ar": "🌱 طلب صلاحية الإنشاء",
        "en": "🌱 Request Creator Access",
    },
    "creator_request.info_text": {
        "fa": (
            "🕋 به ختم‌ساز خوش آمدید!\n\n"
            "ختم‌ساز ابزاری برای برگزاری ختم‌های دسته‌جمعی قرآن، صلوات، دعا و زیارت است.\n\n"
            "📖 ختم تعهدی: سهم مشخصی به شما داده می‌شه و متعهد می‌شید هر روز انجامش بدید.\n"
            "📿 ختم آزاد: به هر اندازه که دوست دارید مشارکت کنید.\n"
            "🌍 ختم عمومی: هر کسی می‌تونه شرکت کنه.\n\n"
            "این بات توسط تیم خدمتگزاران تِک طراحی و ساخته شده. همین حالا ساخت اولین ختم شما شروع می‌شود 👇"
        ),
        "ar": (
            "🕋 مرحباً بك في ختم‌ساز!\n\n"
            "ختم‌ساز هو أداة لإقامة الختمات الجماعية للقرآن، الصلوات، الأدعية والزيارات.\n\n"
            "📖 الختمة الإلزامية: يتم تخصيص ورد محدد تلتزم بأدائه يومياً.\n"
            "📿 الختمة الحرة: يمكنك المشاركة بالقدر الذي ترغب به.\n"
            "🌍 الختمة العامة: يمكن لأي شخص المشاركة.\n\n"
            "تم تصميم هذا البوت بواسطة فريق خدمتگزاران تك. سنبدأ الآن بإنشاء ختمتك الأولى 👇"
        ),
        "en": (
            "🕋 Welcome to KhatmSaz!\n\n"
            "KhatmSaz is a tool for organizing collective recitations of the Quran, Salawat, Duas, and Ziyarats.\n\n"
            "📖 Commitment Khatm: You get a specific portion and commit to doing it daily.\n"
            "📿 Free Khatm: Contribute as much as you like.\n"
            "🌍 Public Khatm: Anyone can participate.\n\n"
            "This bot is developed by the KhedmatGozaran Tech team. Let's create your first Khatm now 👇"
        ),
    },
    "creator_request.submitted": {
        "fa": "درخواست شما ثبت شد و به‌زودی بررسی می‌شه ✅",
        "ar": "تم تسجيل طلبك وسيتم مراجعته قريباً ✅",
        "en": "Your request has been submitted and will be reviewed soon ✅",
    },
    "creator_request.already_pending": {
        "fa": "شما قبلاً یک درخواست در حال بررسی دارید. لطفاً شکیبا باشید ⏳",
        "ar": "لديك طلب قيد المراجعة بالفعل. يرجى الانتظار ⏳",
        "en": "You already have a pending request. Please be patient ⏳",
    },
    "creator_request.approved": {
        "fa": "🎉 درخواست سازنده‌شدن شما تایید شد!\nحالا می‌تونید از منوی اصلی ختم جدید بسازید.",
        "ar": "🎉 تمت الموافقة على طلبك!\nالآن يمكنك إنشاء ختمة جديدة من القائمة الرئيسية.",
        "en": "🎉 Your creator request has been approved!\nYou can now create new khatms from the main menu.",
    },
    "support.menu_text": {
        "fa": "📞 <b>بخش پشتیبانی و ارتباط با ما</b>\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        "ar": "📞 <b>الدعم الفني</b>\n\nالرجاء اختيار أحد الخيارات التالية:",
        "en": "📞 <b>Support & Contact</b>\n\nPlease select an option:",
    },
    "support.button.send_message": {
        "fa": "💬 ارسال تیکت / پیام",
        "ar": "💬 إرسال رسالة",
        "en": "💬 Send a message",
    },
    "button.back": {
        "fa": "🔙 بازگشت",
        "ar": "🔙 رجوع",
        "en": "🔙 Back",
    },
    "button.confirm": {
        "fa": "✅ تأیید و ساخت لینک",
        "ar": "✅ تأكيد وإنشاء الرابط",
        "en": "✅ Confirm & create link",
    },
    "create_khatm.ask_fixed_daily_amount": {
        "fa": "سهم روزانه هر عضو را به صورت یک عدد وارد کنید (مثلاً 100):",
        "ar": "أدخل الحصة اليومية لكل عضو كرقم (مثلاً 100):",
        "en": "Enter the daily share for each member as a number (e.g., 100):",
    },
    "create_khatm.invalid_number": {
        "fa": "لطفاً یک عدد معتبر بزرگتر از صفر وارد کنید.",
        "ar": "يرجى إدخال رقم صحيح أكبر من الصفر.",
        "en": "Please enter a valid number greater than zero.",
    },
    "create_khatm.ask_commitment_policy": {
        "fa": "نحوه مشارکت اعضا را مشخص کنید:\n\nمقدار ثابت روزانه: هر عضو دقیقاً مقداری که شما مشخص می‌کنید را به صورت روزانه قرائت می‌کند.\nانتخاب عضو: هر عضو می‌تواند مدل مشارکت (تعداد آزاد یا برنامه منظم) را خودش انتخاب کند.",
        "ar": "يرجى تحديد سياسة المشاركة للأعضاء:\n\nكمية ثابتة يومياً: يقرأ كل عضو الكمية التي تحددها يومياً.\nاختيار العضو: يمكن لكل عضو اختيار كميته وتكراره بنفسه.",
        "en": "Please specify the participation policy for members:\n\nFixed Daily Amount: Each member reads exactly the amount you specify daily.\nMember Choice: Each member can choose their own amount and frequency.",
    },
    "create_khatm.unit.page": {
        "fa": "صفحه",
        "ar": "صفحة",
        "en": "page",
    },
    "ck.policy.fixed": {
        "fa": "مقدار ثابت روزانه",
        "ar": "كمية يومية ثابتة",
        "en": "Fixed Daily Amount",
    },
    "ck.policy.member_choice": {
        "fa": "انتخاب عضو",
        "ar": "اختيار العضو",
        "en": "Member Choice",
    },
}


def t(key: str, lang: str | None = None, **kwargs) -> str:
    """Return the translated string for `key` in `lang`, falling back to
    Persian if the key or language is missing. Never raises for an unknown
    key/lang — a missing translation should degrade to Persian, not crash
    a live chat."""
    entry = _STRINGS.get(key)
    if entry is None:
        return key
    text = entry.get(lang or _DEFAULT_LANGUAGE) or entry.get(_DEFAULT_LANGUAGE, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text


def variants(key: str) -> frozenset[str]:
    """All language variants of `key`'s text, for matching a reply-keyboard
    button press regardless of which language it was rendered in — see the
    module docstring for why this exists instead of a plain `==` filter."""
    entry = _STRINGS.get(key, {})
    return frozenset(entry.values())
