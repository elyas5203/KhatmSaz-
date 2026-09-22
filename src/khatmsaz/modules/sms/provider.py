"""Vendor-neutral SMS provider contract (ROADMAP Phase 8).

Adding a vendor later means implementing ``SmsProvider.send`` and registering
it in ``build_provider``; reminder and account code must not import vendor
clients directly.
"""

from dataclasses import dataclass
from typing import Protocol

import httpx

from khatmsaz.config import Settings, get_settings


@dataclass(frozen=True)
class SmsSendResult:
    accepted: bool
    provider: str
    message_id: str | None = None
    reason: str | None = None


class SmsProvider(Protocol):
    name: str

    async def send(
        self, *, phone: str, text: str, sender: str | None = None, otp_code: str | None = None,
    ) -> SmsSendResult:
        """Submit one SMS and return a normalized provider result.
        `otp_code`, when given, is the raw verification code this message
        contains — providers that support a pre-approved OTP template
        (e.g. Kavenegar's Verify Lookup, required by Iranian carriers for
        compliance) use it instead of `text`; providers without one just
        ignore it and send `text` as free-form SMS."""


class NoopSmsProvider:
    """Safe default: never sends externally and reports why it did not."""

    name = "noop"

    async def send(
        self, *, phone: str, text: str, sender: str | None = None, otp_code: str | None = None,
    ) -> SmsSendResult:
        return SmsSendResult(
            accepted=False,
            provider=self.name,
            reason="SMS provider is disabled; configure a real vendor first",
        )


class KavenegarSmsProvider:
    """Direct SMS adapter for Kavenegar's REST ``sms/send`` endpoint."""

    name = "kavenegar"

    def __init__(
        self,
        *,
        api_key: str,
        sender: str,
        base_url: str = "https://api.kavenegar.com/v1",
        verify_template: str = "",
        client: httpx.AsyncClient | None = None,
        timeout: float = 15.0,
    ) -> None:
        self._api_key = api_key.strip()
        self._sender = sender.strip()
        self._base_url = base_url.rstrip("/")
        self._verify_template = verify_template.strip()
        self._client = client
        self._timeout = timeout

    @staticmethod
    def _receptor(phone: str) -> str:
        value = phone.strip()
        if value.startswith("+98"):
            return "0" + value[3:]
        return value.removeprefix("+")

    async def send(
        self, *, phone: str, text: str, sender: str | None = None, otp_code: str | None = None,
    ) -> SmsSendResult:
        if not self._api_key:
            return SmsSendResult(accepted=False, provider=self.name, reason="Kavenegar API key is required")
        if otp_code and self._verify_template:
            # Owner request (2026-09-22): a pre-approved OTP pattern
            # ("Verify Lookup") is required by Iranian carriers for
            # compliance — a plain free-text SMS containing a login code
            # is routinely rejected. The pattern's actual wording (e.g.
            # "کد تایید ختم‌ساز: %token%") is configured on Kavenegar's own
            # panel under this template name; we only ever send the name
            # and the raw code, never the wording itself.
            return await self._send_verify_lookup(phone=phone, token=otp_code)
        effective_sender = (sender or self._sender).strip()
        if not effective_sender:
            return SmsSendResult(accepted=False, provider=self.name, reason="Kavenegar sender is required")
        url = f"{self._base_url}/{self._api_key}/sms/send.json"
        payload = {
            "receptor": self._receptor(phone),
            "sender": effective_sender,
            "message": text,
        }
        try:
            if self._client is not None:
                response = await self._client.post(url, data=payload)
            else:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.post(url, data=payload)
            response.raise_for_status()
            body = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            return SmsSendResult(
                accepted=False,
                provider=self.name,
                reason=f"Kavenegar transport/response error: {type(exc).__name__}",
            )

        provider_return = body.get("return") if isinstance(body, dict) else None
        status = provider_return.get("status") if isinstance(provider_return, dict) else None
        if status != 200:
            message = provider_return.get("message") if isinstance(provider_return, dict) else None
            return SmsSendResult(
                accepted=False,
                provider=self.name,
                reason=f"Kavenegar rejected request ({status}): {message or 'unknown error'}",
            )
        entries = body.get("entries") or []
        first = entries[0] if isinstance(entries, list) and entries else {}
        message_id = first.get("messageid") if isinstance(first, dict) else None
        return SmsSendResult(
            accepted=True,
            provider=self.name,
            message_id=str(message_id) if message_id is not None else None,
        )

    async def _send_verify_lookup(self, *, phone: str, token: str) -> SmsSendResult:
        url = f"{self._base_url}/{self._api_key}/verify/lookup.json"
        params = {
            "receptor": self._receptor(phone),
            "token": token,
            "template": self._verify_template,
        }
        try:
            if self._client is not None:
                response = await self._client.get(url, params=params)
            else:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.get(url, params=params)
            response.raise_for_status()
            body = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            return SmsSendResult(
                accepted=False, provider=self.name,
                reason=f"Kavenegar verify-lookup transport/response error: {type(exc).__name__}",
            )
        provider_return = body.get("return") if isinstance(body, dict) else None
        status = provider_return.get("status") if isinstance(provider_return, dict) else None
        if status != 200:
            message = provider_return.get("message") if isinstance(provider_return, dict) else None
            return SmsSendResult(
                accepted=False, provider=self.name,
                reason=f"Kavenegar verify-lookup rejected request ({status}): {message or 'unknown error'}",
            )
        entries = body.get("entries") or []
        first = entries[0] if isinstance(entries, list) and entries else {}
        message_id = first.get("messageid") if isinstance(first, dict) else None
        return SmsSendResult(
            accepted=True, provider=self.name,
            message_id=str(message_id) if message_id is not None else None,
        )


def build_provider(settings: Settings | None = None) -> SmsProvider:
    """Build the configured provider without exposing vendor details upstream."""
    settings = settings or get_settings()
    provider_name = settings.sms_provider.strip().lower()
    if provider_name in {"", "noop", "disabled"}:
        return NoopSmsProvider()
    if provider_name == "kavenegar":
        return KavenegarSmsProvider(
            api_key=settings.sms_api_key,
            verify_template=getattr(settings, "sms_kavenegar_verify_template", ""),
            sender=settings.sms_sender,
            base_url=getattr(
                settings, "sms_api_base_url", "https://api.kavenegar.com/v1"
            ),
        )
    raise ValueError(
        f"Unsupported SMS_PROVIDER={settings.sms_provider!r}; install an adapter or use 'noop'"
    )
