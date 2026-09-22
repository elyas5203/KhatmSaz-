"""Security contract for Telegram Mini App authentication."""

from datetime import datetime, timezone
import hashlib
import hmac
import json
from urllib.parse import urlencode

import pytest

from khatmsaz.web.telegram_mini_app import InvalidTelegramInitData, validate_telegram_init_data


TOKEN = "123456:test-token"
NOW = datetime(2026, 9, 20, 12, 0, tzinfo=timezone.utc)


def _signed(**overrides) -> str:
    values = {
        "auth_date": str(int(NOW.timestamp())),
        "query_id": "AAH-test-query",
        "user": json.dumps(
            {"id": 8852949283, "first_name": "Elyas", "username": "owner"},
            separators=(",", ":"),
        ),
        **overrides,
    }
    check = "\n".join(f"{key}={value}" for key, value in sorted(values.items()))
    secret = hmac.new(b"WebAppData", TOKEN.encode(), hashlib.sha256).digest()
    values["hash"] = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    return urlencode(values)


def test_valid_signed_launch_returns_only_authenticated_identity():
    user = validate_telegram_init_data(_signed(), TOKEN, now=NOW)
    assert user.id == 8852949283
    assert user.first_name == "Elyas"
    assert user.username == "owner"


@pytest.mark.parametrize(
    "value",
    [
        lambda: _signed().replace("Elyas", "Mallory"),
        lambda: _signed(auth_date=str(int(NOW.timestamp()) - 301)),
        lambda: _signed() + "&user=%7B%22id%22%3A1%7D",
        lambda: "auth_date=1&user=%7B%22id%22%3A1%7D&hash=bad",
    ],
)
def test_forged_stale_duplicate_and_malformed_launches_fail_closed(value):
    with pytest.raises(InvalidTelegramInitData):
        validate_telegram_init_data(value(), TOKEN, now=NOW)


def test_wrong_bot_token_cannot_authenticate():
    with pytest.raises(InvalidTelegramInitData):
        validate_telegram_init_data(_signed(), "999999:other-bot", now=NOW)
