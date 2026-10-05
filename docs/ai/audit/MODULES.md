# نقشهٔ دقیق پوشه‌ها و تست‌های نامزد

تعدادها برای snapshot در SNAPSHOT.json هستند؛ تطبیق نام تست فقط سرنخ است، نه اثبات پوشش. همهٔ توابع و خط‌ها در ITEMS.csv آمده‌اند. برای خواندن هر فایل از مسیر ریشه استفاده کنید.

| مسیر | فایل | تابع | فایل‌های تست نامزد (نام مشترک) |
|---|---:|---:|---|
| `src/khatmsaz/modules/account_merge` | 2 | 0 | نیازمند نگاشت دستی از callers و assertionها |
| `src/khatmsaz/modules/advertising` | 3 | 3 | `tests/test_advertising_rewards_integration.py` |
| `src/khatmsaz/modules/allocation` | 4 | 45 | `tests/test_rotating_quran_allocation_integration.py` |
| `src/khatmsaz/modules/audit_log` | 4 | 4 | نیازمند نگاشت دستی از callers و assertionها |
| `src/khatmsaz/modules/authorization` | 4 | 9 | `tests/test_private_join_authorization.py`، `tests/test_private_join_authorization_integration.py` |
| `src/khatmsaz/modules/bot_registry` | 4 | 20 | نیازمند نگاشت دستی از callers و assertionها |
| `src/khatmsaz/modules/broadcast` | 4 | 17 | `tests/test_broadcast_integration.py`، `tests/test_broadcast_policy.py`، `tests/test_broadcast_target_picker.py` |
| `src/khatmsaz/modules/completion` | 2 | 2 | `tests/test_completion_announcement_integration.py`، `tests/test_khatm_completion_integration.py` |
| `src/khatmsaz/modules/content` | 6 | 36 | `tests/test_committed_quran_auto_content_push_integration.py`، `tests/test_content_preferences_integration.py`، `tests/test_fixed_salawat_content.py` |
| `src/khatmsaz/modules/creator_broadcast` | 0 | 0 | نیازمند نگاشت دستی از callers و assertionها |
| `src/khatmsaz/modules/creator_request` | 4 | 11 | نیازمند نگاشت دستی از callers و assertionها |
| `src/khatmsaz/modules/identity` | 4 | 26 | `tests/test_identity_search_integration.py` |
| `src/khatmsaz/modules/invitation` | 4 | 6 | نیازمند نگاشت دستی از callers و assertionها |
| `src/khatmsaz/modules/khatm` | 6 | 48 | `tests/test_admin_khatm_search_integration.py`، `tests/test_create_khatm_survives_phone_verification.py`، `tests/test_default_khatm_title.py`، `tests/test_khatm_category_group_integration.py`، `tests/test_khatm_completion_integration.py`، `tests/test_khatm_cosmetic_edit_integration.py`، `tests/test_khatm_cover_moderation_integration.py`، `tests/test_khatm_end_at_integration.py`، `tests/test_khatm_refund_integration.py`، `tests/test_khatm_request_attachment_integration.py`، `tests/test_khatm_stats_integration.py`، `tests/test_my_khatms_hierarchy_integration.py`، `tests/test_paid_khatm_invoice_integration.py`، `tests/test_public_khatms_button.py`، `tests/test_public_khatms_integration.py`، `tests/test_reminder_settings_per_khatm.py` |
| `src/khatmsaz/modules/khatm_category` | 3 | 23 | `tests/test_khatm_category_group_integration.py` |
| `src/khatmsaz/modules/khatm_request` | 4 | 9 | `tests/test_khatm_request_attachment_integration.py` |
| `src/khatmsaz/modules/khatm_workflow` | 2 | 13 | نیازمند نگاشت دستی از callers و assertionها |
| `src/khatmsaz/modules/manual_phone_verification` | 4 | 9 | `tests/test_manual_phone_verification_integration.py` |
| `src/khatmsaz/modules/message_template` | 4 | 9 | `tests/test_message_template.py`، `tests/test_message_template_management_integration.py` |
| `src/khatmsaz/modules/monthly_report` | 2 | 3 | `tests/test_monthly_report_integration.py` |
| `src/khatmsaz/modules/notification` | 4 | 15 | `tests/test_notification_snooze.py` |
| `src/khatmsaz/modules/open_contribution` | 4 | 18 | نیازمند نگاشت دستی از callers و assertionها |
| `src/khatmsaz/modules/participation` | 5 | 51 | نیازمند نگاشت دستی از callers و assertionها |
| `src/khatmsaz/modules/phone` | 4 | 23 | `tests/test_create_khatm_survives_phone_verification.py`، `tests/test_manual_phone_verification_integration.py`، `tests/test_manual_phone_web_integration.py`، `tests/test_phone_otp_integration.py`، `tests/test_registration_phone_share_only.py` |
| `src/khatmsaz/modules/plan` | 4 | 15 | `tests/test_admin_finance_plans_web_integration.py`، `tests/test_plan_entitlements_integration.py`، `tests/test_plan_family_cap_integration.py`، `tests/test_pro_plan_purchase.py` |
| `src/khatmsaz/modules/reminder_engine` | 2 | 19 | نیازمند نگاشت دستی از callers و assertionها |
| `src/khatmsaz/modules/reporting` | 2 | 5 | `tests/test_reporting_integration.py` |
| `src/khatmsaz/modules/servant_ad` | 2 | 6 | `tests/test_servant_ad.py` |
| `src/khatmsaz/modules/session` | 4 | 10 | `tests/test_admin_session_integration.py` |
| `src/khatmsaz/modules/settings` | 4 | 14 | `tests/test_reminder_settings_per_khatm.py`، `tests/test_settings_language.py`، `tests/test_sms_settings_integration.py`، `tests/test_system_settings_strings.py` |
| `src/khatmsaz/modules/share_occurrence` | 4 | 16 | `tests/test_share_occurrence_integration.py` |
| `src/khatmsaz/modules/sms` | 2 | 7 | `tests/test_sms_provider.py`، `tests/test_sms_settings_integration.py`، `tests/test_sms_subscription_safety_integration.py` |
| `src/khatmsaz/modules/sms_subscription` | 3 | 13 | `tests/test_sms_subscription_safety_integration.py` |
| `src/khatmsaz/modules/system_settings` | 4 | 8 | `tests/test_system_settings_strings.py` |
| `src/khatmsaz/modules/waiting_list` | 4 | 4 | نیازمند نگاشت دستی از callers و assertionها |
| `src/khatmsaz/modules/wallet` | 6 | 49 | `tests/test_wallet_payment_integration.py` |
| `src/khatmsaz/bot/handlers` | 41 | 482 | نیازمند نگاشت دستی از callers و assertionها |
| `src/khatmsaz/core` | 8 | 23 | نیازمند نگاشت دستی از callers و assertionها |
| `src/khatmsaz/web` | 35 | 93 | `tests/test_admin_finance_plans_web_integration.py`، `tests/test_admin_web_integration.py`، `tests/test_creator_web_integration.py`، `tests/test_manual_phone_web_integration.py` |
| `src/khatmsaz/i18n` | 1 | 2 | `tests/test_i18n_audit.py`، `tests/test_i18n_coverage.py`، `tests/test_registration_i18n_integration.py`، `tests/test_wizard_keyboards_i18n.py` |
| `migrations` | 86 | 171 | نیازمند نگاشت دستی از callers و assertionها |
| `tests` | 146 | 718 | نیازمند نگاشت دستی از callers و assertionها |
| `scripts` | 4 | 7 | نیازمند نگاشت دستی از callers و assertionها |

## فایل‌های entry point و رابط‌ها

| مسیر دقیق | تعداد توابع |
|---|---:|
| `src/khatmsaz/bootstrap.py` | 6 |
| `src/khatmsaz/bot/handlers/__init__.py` | 0 |
| `src/khatmsaz/bot/handlers/account.py` | 5 |
| `src/khatmsaz/bot/handlers/account_link.py` | 4 |
| `src/khatmsaz/bot/handlers/admin.py` | 41 |
| `src/khatmsaz/bot/handlers/broadcast.py` | 6 |
| `src/khatmsaz/bot/handlers/change_phone.py` | 12 |
| `src/khatmsaz/bot/handlers/content_settings.py` | 5 |
| `src/khatmsaz/bot/handlers/create_khatm.py` | 86 |
| `src/khatmsaz/bot/handlers/creator_broadcast.py` | 6 |
| `src/khatmsaz/bot/handlers/creator_decisions.py` | 2 |
| `src/khatmsaz/bot/handlers/creator_request.py` | 5 |
| `src/khatmsaz/bot/handlers/devotional.py` | 5 |
| `src/khatmsaz/bot/handlers/digest_settings.py` | 1 |
| `src/khatmsaz/bot/handlers/font_settings.py` | 1 |
| `src/khatmsaz/bot/handlers/help.py` | 5 |
| `src/khatmsaz/bot/handlers/join_flow.py` | 7 |
| `src/khatmsaz/bot/handlers/join_requests.py` | 5 |
| `src/khatmsaz/bot/handlers/khatm_request.py` | 12 |
| `src/khatmsaz/bot/handlers/language_settings.py` | 1 |
| `src/khatmsaz/bot/handlers/leave.py` | 7 |
| `src/khatmsaz/bot/handlers/manage_content.py` | 4 |
| `src/khatmsaz/bot/handlers/manual_phone_verification.py` | 5 |
| `src/khatmsaz/bot/handlers/member_commitment.py` | 25 |
| `src/khatmsaz/bot/handlers/member_my_khatms.py` | 3 |
| `src/khatmsaz/bot/handlers/member_registration.py` | 14 |
| `src/khatmsaz/bot/handlers/member_start.py` | 6 |
| `src/khatmsaz/bot/handlers/my_khatms.py` | 49 |
| `src/khatmsaz/bot/handlers/panel.py` | 18 |
| `src/khatmsaz/bot/handlers/portions.py` | 32 |
| `src/khatmsaz/bot/handlers/profile.py` | 12 |
| `src/khatmsaz/bot/handlers/public_khatms.py` | 3 |
| `src/khatmsaz/bot/handlers/reciter_settings.py` | 1 |
| `src/khatmsaz/bot/handlers/registration.py` | 12 |
| `src/khatmsaz/bot/handlers/reminder_settings.py` | 1 |
| `src/khatmsaz/bot/handlers/report.py` | 7 |
| `src/khatmsaz/bot/handlers/settings_menu.py` | 31 |
| `src/khatmsaz/bot/handlers/sms_settings.py` | 1 |
| `src/khatmsaz/bot/handlers/start.py` | 17 |
| `src/khatmsaz/bot/handlers/suggestions.py` | 10 |
| `src/khatmsaz/bot/handlers/timezone_settings.py` | 1 |
| `src/khatmsaz/bot/handlers/wallet.py` | 14 |
| `src/khatmsaz/web/__init__.py` | 0 |
| `src/khatmsaz/web/app.py` | 92 |
| `src/khatmsaz/web/static/app.css` | 0 |
| `src/khatmsaz/web/static/devotional-images/.gitignore` | 0 |
| `src/khatmsaz/web/static/devotional-images/README.md` | 0 |
| `src/khatmsaz/web/static/finance.css` | 0 |
| `src/khatmsaz/web/telegram_mini_app.py` | 1 |
| `src/khatmsaz/web/templates/admins.html` | 0 |
| `src/khatmsaz/web/templates/audit.html` | 0 |
| `src/khatmsaz/web/templates/base.html` | 0 |
| `src/khatmsaz/web/templates/bot_tokens.html` | 0 |
| `src/khatmsaz/web/templates/broadcasts.html` | 0 |
| `src/khatmsaz/web/templates/categories.html` | 0 |
| `src/khatmsaz/web/templates/components.html` | 0 |
| `src/khatmsaz/web/templates/creator_base.html` | 0 |
| `src/khatmsaz/web/templates/creator_broadcasts.html` | 0 |
| `src/khatmsaz/web/templates/creator_dashboard.html` | 0 |
| `src/khatmsaz/web/templates/creator_khatm_detail.html` | 0 |
| `src/khatmsaz/web/templates/creator_khatm_new.html` | 0 |
| `src/khatmsaz/web/templates/creator_khatms.html` | 0 |
| `src/khatmsaz/web/templates/creator_login.html` | 0 |
| `src/khatmsaz/web/templates/creator_requests.html` | 0 |
| `src/khatmsaz/web/templates/creator_wallet.html` | 0 |
| `src/khatmsaz/web/templates/dashboard.html` | 0 |
| `src/khatmsaz/web/templates/devotionals.html` | 0 |
| `src/khatmsaz/web/templates/finance.html` | 0 |
| `src/khatmsaz/web/templates/khatm_detail.html` | 0 |
| `src/khatmsaz/web/templates/khatms.html` | 0 |
| `src/khatmsaz/web/templates/login.html` | 0 |
| `src/khatmsaz/web/templates/mini_app_login.html` | 0 |
| `src/khatmsaz/web/templates/operations.html` | 0 |
| `src/khatmsaz/web/templates/phone_verifications.html` | 0 |
| `src/khatmsaz/web/templates/servant_ad.html` | 0 |
| `src/khatmsaz/web/templates/templates.html` | 0 |
| `src/khatmsaz/web/templates/users.html` | 0 |
