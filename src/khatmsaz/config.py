"""Central application settings, loaded once from environment / .env.

Every other module reads configuration through `get_settings()` — never
`os.environ` directly — so there is exactly one place that knows how
configuration is sourced.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://khatmsaz:khatmsaz@localhost:5432/khatmsaz"
    redis_url: str = "redis://localhost:6379/0"

    telegram_bot_token: str = ""
    telegram_bot_username: str = ""
    # Private channel containing the canonical 604-page Quran image/audio
    # posts. The bot itself must be a member before it can forward messages.
    quran_source_telegram_chat_id: int = -1001127138974

    bale_bot_token: str = ""
    bale_api_base_url: str = "https://tapi.bale.ai"
    bale_bot_username: str = ""

    admin_web_enabled: bool = True
    admin_web_host: str = "0.0.0.0"
    admin_web_port: int = 8000
    # Public HTTPS origin opened by Telegram/Bale Mini App buttons. Local
    # HTTP addresses are deliberately rejected by the bot handlers.
    admin_web_base_url: str = ""
    # Public, HTTPS origin used for shareable invitation landing pages.
    # Keep empty in local development so creators receive direct bot links.
    public_web_base_url: str = ""

    # Local-dev-only escape hatch: some networks (e.g. Telegram is blocked
    # without a VPN in Iran) resolve api.telegram.org to a private "fake IP"
    # that only a local VPN/proxy client can route. If outbound requests to
    # Telegram/Bale hang or get refused, point this at that client's local
    # HTTP proxy (see DEBUGGING.md "Bot can't reach Telegram on Windows").
    # Leave empty on a real server with unblocked internet access.
    bot_http_proxy_url: str = ""

    otp_hmac_secret: str = ""
    dev_otp: bool = False

    sms_provider: str = "noop"
    sms_api_key: str = ""
    sms_sender: str = ""
    sms_api_base_url: str = "https://api.kavenegar.com/v1"
    # Owner request (2026-09-22): Iranian providers (Kavenegar included)
    # generally require OTP codes to go through a pre-approved pattern
    # ("Verify Lookup"), not the generic free-text send endpoint — plain
    # SMS containing a login/verification code is routinely rejected by
    # carriers for compliance. When set, this names that approved pattern
    # (the owner registered one called "verify" whose body is
    # "کد تایید ختم‌ساز: %token%") and OTP sends use Kavenegar's
    # verify/lookup.json endpoint instead of sms/send.json.
    sms_kavenegar_verify_template: str = ""

    zarinpal_merchant_id: str = ""
    zarinpal_sandbox: bool = True
    # PayPing requires a dedicated bearer/API token. Panel login credentials
    # are intentionally not application configuration.
    payping_api_token: str = ""
    payping_callback_url: str = "https://khatmsaz.com/payments/payping/callback"

    # Cost to create a khatm, deducted from the creator's wallet
    # (credit_toman first, then balance_toman — see wallet.service.spend).
    # Defaults to 0 (free) until PayPing has a dedicated API token and the
    # public HTTPS callback has been verified end-to-end. Raise this only
    # after users can reliably top up their wallet.
    # See DECISIONS.md DEC-PY-0012.
    khatm_creation_price_toman: int = 0

    # Comma-separated Telegram chat ids (numeric, no @username) — whoever's
    # id is listed here is auto-promoted to SUPER_ADMIN the next time they
    # message the bot. No admin panel exists yet, so this is how the first
    # admin gets bootstrapped. See DECISIONS.md DEC-PY-0013.
    super_admin_telegram_chat_ids: str = ""
    # Same idea, separate list, for Bale chat ids (owner request, 2026-09-22
    # — Bale bot activated). Kept as its own field rather than merging with
    # the Telegram list because a numeric chat id is only meaningful within
    # one platform; treating them as one list could accidentally promote
    # the wrong person if the ids ever coincide.
    super_admin_bale_chat_ids: str = ""

    # Fernet key for encrypting member bot tokens stored in `bot_instances`.
    # Generate once: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    bot_token_encryption_key: str = ""

    app_timezone: str = "Asia/Tehran"
    log_level: str = "INFO"

    # How often the reminder/deadline-miss scan runs (reminder_engine).
    # Every hour is enough in production (reminders/deadlines are hour-
    # granular); a smaller value is useful only for manual testing.
    reminder_scan_interval_minutes: int = 30
    monthly_report_day: int = 1
    monthly_report_hour: int = 10


@lru_cache
def get_settings() -> Settings:
    return Settings()
