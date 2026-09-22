"""Contract tests for the PayPing v3 adapter, without live financial calls."""

import httpx
import pytest

from khatmsaz.modules.wallet.gateway import GatewayError
from khatmsaz.modules.wallet.payping import PayPingGateway


@pytest.mark.asyncio
async def test_payping_v3_request_uses_toman_client_reference_and_bearer_token():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["request"] = request
        seen["payload"] = __import__("json").loads(request.content)
        return httpx.Response(
            200,
            json={
                "paymentCode": "payment-code-1",
                "url": "https://api.payping.ir/v3/pay/start/payment-code-1",
                "amount": 50_000,
                "payerWage": 0,
                "businessWage": 0,
                "gatewayAmount": 50_000,
                "paypingVat": 0,
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        gateway = PayPingGateway("test-token", client=client)
        result = await gateway.request_payment(
            amount_toman=50_000,
            description="شارژ تست",
            callback_url="https://khatmsaz.com/payments/payping/callback",
            client_ref_id="local-reference",
        )

    assert seen["request"].url.path == "/v3/pay"
    assert seen["request"].headers["authorization"] == "Bearer test-token"
    assert seen["payload"]["amount"] == 50_000
    assert seen["payload"]["clientRefId"] == "local-reference"
    assert seen["payload"]["returnUrl"].endswith("/payments/payping/callback")
    assert result.authority == "payment-code-1"
    assert result.payment_url.startswith("https://")


@pytest.mark.asyncio
async def test_payping_v3_verify_checks_every_bound_field():
    def handler(request: httpx.Request) -> httpx.Response:
        payload = __import__("json").loads(request.content)
        assert request.url.path == "/v3/pay/verify"
        assert payload == {
            "paymentRefId": 987654,
            "paymentCode": "payment-code-1",
            "amount": 50_000,
        }
        return httpx.Response(
            200,
            json={
                "amount": 50_000,
                "clientRefId": "local-reference",
                "paymentRefId": 987654,
                "code": "payment-code-1",
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await PayPingGateway("test-token", client=client).verify_payment(
            authority="payment-code-1",
            amount_toman=50_000,
            transaction_ref="987654",
            client_ref_id="local-reference",
        )
    assert result.transaction_ref == "987654"


@pytest.mark.asyncio
async def test_payping_rejects_mismatched_or_insecure_response():
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "paymentCode": "payment-code-1",
                "url": "http://not-secure.invalid/pay",
                "amount": 50_000,
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(GatewayError):
            await PayPingGateway("test-token", client=client).request_payment(
                amount_toman=50_000,
                description="test",
                callback_url="https://khatmsaz.com/payments/payping/callback",
                client_ref_id="local-reference",
            )


@pytest.mark.asyncio
async def test_payping_error_keeps_trace_id_but_never_token():
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            json={
                "paypingTraceId": "trace-for-support",
                "metaData": {"code": 105, "errors": [{"message": "invalid callback"}]},
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(GatewayError) as caught:
            await PayPingGateway("super-secret-token", client=client).request_payment(
                amount_toman=50_000,
                description="test",
                callback_url="https://khatmsaz.com/payments/payping/callback",
                client_ref_id="local-reference",
            )
    assert "trace-for-support" in str(caught.value)
    assert "super-secret-token" not in str(caught.value)
