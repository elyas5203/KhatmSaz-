# BUTTON_AUDIT — ممیزیِ دکمه‌ها و منوها (OWNER_SPEC_MASTER §N5)

> هر ردیف: محل · متن دکمه · callback/filter · شخصیتِ مجاز · می‌فرستد به/کارش ·
> وضعیت (✅ درست · ⚠️ بهبود · ❌ باگ). تاریخ: ۲۰۲۶-۱۰-۰۱ [Claude Code]. ادامه‌دار.

## ۱) بات ختم‌ساز — منوی reply سازنده (`keyboards.creator_menu_keyboard`)
| دکمه | هندلر | وضعیت |
|---|---|---|
| ➕ ساخت ختم جدید | `create_khatm.start_wizard` (F.text menu.create) | ✅ |
| 👑 مدیریت ختم‌ها | `panel.handle_creator_management` → creator_management_keyboard | ✅ |
| 📊 گزارش و مالی | `panel.handle_creator_finance` → report | ✅ |
| ⚙️ تنظیمات حساب | `settings_menu.settings_overview` | ✅ (دکمهٔ «ورود به پنل سازنده» برای سازنده هست) |
| ❓ راهنما و پشتیبانی | `panel.handle_creator_support` → help | ✅ |

### منوی مدیریت (`creator_management_keyboard`)
| ➕ ساخت / 🕋 ختم‌های من / 📢 ارسال پیام گروهی / 🔙 بازگشت | create/my_khatms/creator_broadcast/back | ✅ (L9: پیام گروهی اینجا هست؛ مدیا هم می‌پذیرد) |

### منوی مالی (`creator_finance_keyboard`)
| 📈 گزارش / 💳 شارژ کیف پول / 🔙 | report / wallet._show_wallet / back | ✅ |

### پنل اینلاین سازنده (`panel.creator_panel_keyboard`)
| باز کردن مینی‌اپ (creator:web_login) / ساخت / ختم‌های من / پیام گروهی / گزارش / کیف پول / تنظیمات | همه به هندلرهای واقعی وصل | ✅ |

## ۲) بات‌های ممبر — منوی reply (`keyboards.member_menu_keyboard`)
| 📅 امروز | `report.today_overview` | ⚠️ باید L5/N4: نام «انجام قرائت امروز» و عدم‌تکرارِ نمایش سهم بررسی شود |
| 🕋 ختم‌های من | `member_my_khatms.list_member_khatms` (+/my_khatms) | ✅ |
| 🌍 ختم‌های عمومی | `public_khatms.list_public_khatms` | ✅ |
| ⚙️ تنظیمات حساب | settings_menu | ✅ (دکمهٔ پنل سازنده برای ممبر پنهان است) |
| ✉️ ارتباط با سازندهٔ ختم | `suggestions.start_creator_contact` | ✅ (تیکت به سازنده) |

### جوین (member_start / start)
| دکمهٔ شرکت/جوین، consent، ساعت، سهم | join_flow/start | ⚠️ N4: محتوای سهم نباید دوبار بیاید |

## ۳) پنل ادمین (وب) — لینک‌های ناوبری
همه روت دارند و تمپلیت رندر می‌شود (ممیزی خودکار TEST_CHECKLIST). دکمه‌های فرم:
مالی/دسته‌ها/دعاها/پیام‌ها/باتها/کاربران/احراز/پیام‌گروهی/تبلیغ‌خدمتگزاران/
سلامت/رویدادها/مدیران → ✅ روت موجود.
- پنل اینلاینِ ادمینِ بات (`admin_panel:users`/`:broadcast`) = پیامِ راهنما به
  سمت پنل وب (⚠️ بن‌بستِ ملایم — عمداً، چون کار اصلی در وب است).

## ۴) پنل کریتور (وب) — ناوبری + فرم‌ها
خانه/ختم‌ها/کیف پول/ساخت ختم جدید/جزئیات ختم → ✅ روت + رندر.

## موارد باز (برای ادامه)
- ❌/⚠️ N4: عدم‌تکرارِ نمایشِ سهم در «امروز» (کد: `report.deliver_today_early`).
- ⬜ N3b: مخفی‌سازیِ هر انتخاب/نمایشِ زبانِ عربی/انگلیسی در settings و help و member bots.
- ⬜ ممیزیِ دکمه‌به‌دکمهٔ ویزارد ساخت (back در هر مرحله) و دکمه‌های سهم/قرائت.
