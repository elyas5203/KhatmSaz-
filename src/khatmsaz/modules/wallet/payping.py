"""PayPing v3 payment-gateway adapter.

The endpoint names and payloads follow PayPing's official v3 API
specification.  All amounts in that API are Toman.
"""

from __future__ import annotations

from typing import Any

import httpx

from khatmsaz.modules.wallet.gateway import (
    GatewayError,
    PaymentRequest,
    PaymentVerification,
)


class PayPingGateway:
    API_BASE_URL = "https://api.payping.ir"

    def __init__(
        self,
        token: str,
        *,
        client: httpx.AsyncClient | None = None,
        api_base_url: str = API_BASE_URL,
        timeout_seconds: float = 15.0,
    ) -> None:
        if not token.strip():
            raise ValueError("PayPing API token is required")
        self._token = token.strip()
        self._client = client
        self._api_base_url = api_base_url.rstrip("/")
        self._timeout = timeout_seconds

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def _post(self, path: str, payload: dict[str, Any]) -> httpx.Response:
        try:
            if self._client is not None:
                return await self._client.post(
                    f"{self._api_base_url}{path}", json=payload, headers=self._headers
                )
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                return await client.post(
                    f"{self._api_base_url}{path}", json=payload, headers=self._headers
                )
        except httpx.HTTPError as exc:
            raise GatewayError("ارتباط امن با پی‌پینگ برقرار نشد.") from exc

    @staticmethod
    def _json(response: httpx.Response) -> dict[str, Any]:
        try:
            data = response.json()
        except ValueError as exc:
            raise GatewayError("پاسخ نامعتبر از پی‌پینگ دریافت شد.") from exc
        if not isinstance(data, dict):
            raise GatewayError("ساختار پاسخ پی‌پینگ نامعتبر است.")
        return data

    @classmethod
    def _raise_for_error(cls, response: httpx.Response) -> None:
        if 200 <= response.status_code < 300:
            return
        trace_id = ""
        error_code = ""
        try:
            data = cls._json(response)
            trace_id = str(data.get("paypingTraceId") or "")
            metadata = data.get("metaData")
            if isinstance(metadata, dict):
                error_code = str(metadata.get("code") or "")
        except GatewayError:
            pass
        suffix = ""
        if error_code:
            suffix += f" کد خطا: {error_code}."
        if trace_id:
            suffix += f" شناسه پیگیری: {trace_id}."
        raise GatewayError(f"پی‌پینگ درخواست را نپذیرفت (HTTP {response.status_code}).{suffix}")

    async def request_payment(
        self,
        *,
        amount_toman: int,
        description: str,
        callback_url: str,
        client_ref_id: str,
    ) -> PaymentRequest:
        response = await self._post(
            "/v3/pay",
            {
                "amount": amount_toman,
                "returnUrl": callback_url,
                "description": description,
                "clientRefId": client_ref_id,
                "isReversible": False,
                "IsBlocked": False,
            },
        )
        self._raise_for_error(response)
        data = self._json(response)
        authority = str(data.get("paymentCode") or "").strip()
        payment_url = str(data.get("url") or "").strip()
        returned_amount = data.get("amount")
        if not authority or not payment_url or returned_amount != amount_toman:
            raise GatewayError("پاسخ ساخت پرداخت پی‌پینگ با درخواست تطبیق ندارد.")
        if not payment_url.startswith("https://"):
            raise GatewayError("آدرس پرداخت امن از پی‌پینگ دریافت نشد.")
        return PaymentRequest(authority=authority, payment_url=payment_url)

    async def verify_payment(
        self,
        *,
        authority: str,
        amount_toman: int,
        transaction_ref: str,
        client_ref_id: str,
    ) -> PaymentVerification:
        try:
            payment_ref_id = int(transaction_ref)
        except (TypeError, ValueError) as exc:
            raise GatewayError("شناسه تراکنش پی‌پینگ نامعتبر است.") from exc
        response = await self._post(
            "/v3/pay/verify",
            {
                "paymentRefId": payment_ref_id,
                "paymentCode": authority,
                "amount": amount_toman,
            },
        )
        self._raise_for_error(response)
        data = self._json(response)
        response_authority = str(data.get("code") or "").strip()
        response_ref = str(data.get("paymentRefId") or "").strip()
        response_client_ref = str(data.get("clientRefId") or "").strip()
        if (
            response_authority != authority
            or data.get("amount") != amount_toman
            or response_ref != transaction_ref
            or response_client_ref != client_ref_id
        ):
            raise GatewayError("پاسخ تأیید پی‌پینگ با پرداخت ذخیره‌شده تطبیق ندارد.")
        return PaymentVerification(
            authority=authority,
            amount_toman=amount_toman,
            transaction_ref=transaction_ref,
        )
