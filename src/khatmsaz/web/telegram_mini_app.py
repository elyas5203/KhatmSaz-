"""Validation for Telegram Mini App signed launch data."""

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
from urllib.parse import parse_qsl


class InvalidTelegramInitData(ValueError):
    """The launch data is malformed, stale, or has an invalid signature."""


@dataclass(frozen=True)
class TelegramMiniAppUser:
    id: int
    first_name: str = ""
    last_name: str = ""
    username: str = ""


def validate_telegram_init_data(
    init_data: str,
    bot_token: str,
    *,
    now: datetime | None = None,
    max_age_seconds: int = 300,
    future_skew_seconds: int = 30,
) -> TelegramMiniAppUser:
    """Validate Telegram's HMAC and return its authenticated user."""
    if not init_data or not bot_token:
        raise InvalidTelegramInitData("missing signed launch data")
    try:
        pairs = parse_qsl(init_data, keep_blank_values=True, strict_parsing=True)
    except ValueError:
        raise InvalidTelegramInitData("malformed launch data") from None
    keys = [key for key, _ in pairs]
    if len(keys) != len(set(keys)):
        raise InvalidTelegramInitData("duplicate launch-data field")
    values = dict(pairs)
    received_hash = values.pop("hash", "")
    if len(received_hash) != 64:
        raise InvalidTelegramInitData("invalid launch-data signature")

    data_check_string = "\n".join(
        f"{key}={value}" for key, value in sorted(values.items())
    )
    secret_key = hmac.new(
        b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256
    ).digest()
    expected_hash = hmac.new(
        secret_key, data_check_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(received_hash.lower(), expected_hash):
        raise InvalidTelegramInitData("invalid launch-data signature")

    try:
        auth_date = int(values["auth_date"])
        user_data = json.loads(values["user"])
        user_id = int(user_data["id"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        raise InvalidTelegramInitData("invalid launch-data identity") from None
    if user_id <= 0 or not isinstance(user_data, dict):
        raise InvalidTelegramInitData("invalid launch-data identity")

    current = now or datetime.now(timezone.utc)
    age = int(current.timestamp()) - auth_date
    if age > max_age_seconds or age < -future_skew_seconds:
        raise InvalidTelegramInitData("expired launch data")
    return TelegramMiniAppUser(
        id=user_id,
        first_name=str(user_data.get("first_name") or ""),
        last_name=str(user_data.get("last_name") or ""),
        username=str(user_data.get("username") or ""),
    )
