import pytest
import httpx

from khatmsaz.modules.sms.provider import (
    KavenegarSmsProvider,
    NoopSmsProvider,
    SmsSendResult,
    build_provider,
)


@pytest.mark.asyncio
async def test_noop_sms_provider_never_sends_and_returns_normalized_result():
    result = await NoopSmsProvider().send(phone="+989121234567", text="سلام")
    assert result == SmsSendResult(
        accepted=False,
        provider="noop",
        reason="SMS provider is disabled; configure a real vendor first",
    )


def test_provider_factory_defaults_to_noop():
    class SettingsStub:
        sms_provider = "noop"

    assert isinstance(build_provider(SettingsStub()), NoopSmsProvider)


def test_provider_factory_rejects_unknown_vendor():
    class SettingsStub:
        sms_provider = "unknown-vendor"

    with pytest.raises(ValueError, match="Unsupported SMS_PROVIDER"):
        build_provider(SettingsStub())


@pytest.mark.asyncio
async def test_kavenegar_provider_sends_form_and_normalizes_success():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/v1/secret-key/sms/send.json"
        form = dict(item.split("=", 1) for item in request.content.decode().split("&"))
        assert form["receptor"] == "09121234567"
        assert form["sender"] == "10001234"
        return httpx.Response(
            200,
            json={
                "return": {"status": 200, "message": "تایید شد"},
                "entries": [{"messageid": 987654321, "status": 1}],
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = KavenegarSmsProvider(
            api_key="secret-key", sender="10001234", client=client
        )
        result = await provider.send(phone="+989121234567", text="رمز: 123456")
    assert result == SmsSendResult(
        accepted=True, provider="kavenegar", message_id="987654321"
    )


@pytest.mark.asyncio
async def test_kavenegar_provider_normalizes_api_rejection_without_leaking_key():
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"return": {"status": 411, "message": "گیرنده نامعتبر است"}, "entries": []},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = KavenegarSmsProvider(
            api_key="never-expose-this", sender="10001234", client=client
        )
        result = await provider.send(phone="+989121234567", text="test")
    assert result.accepted is False
    assert result.provider == "kavenegar"
    assert "411" in result.reason
    assert "never-expose-this" not in result.reason


@pytest.mark.asyncio
async def test_kavenegar_provider_fails_closed_when_configuration_missing():
    provider = KavenegarSmsProvider(api_key="", sender="")
    result = await provider.send(phone="+989121234567", text="test")
    assert result.accepted is False
    assert result.reason == "Kavenegar API key is required"

    provider = KavenegarSmsProvider(api_key="key", sender="")
    result = await provider.send(phone="+989121234567", text="test")
    assert result.accepted is False
    assert result.reason == "Kavenegar sender is required"


def test_provider_factory_builds_kavenegar():
    class SettingsStub:
        sms_provider = "kavenegar"
        sms_api_key = "key"
        sms_sender = "10001234"
        sms_api_base_url = "https://api.kavenegar.com/v1"

    assert isinstance(build_provider(SettingsStub()), KavenegarSmsProvider)


@pytest.mark.asyncio
async def test_kavenegar_uses_verify_lookup_when_otp_code_and_template_given():
    """Owner request (2026-09-22): Iranian carriers require OTP codes to
    go through a pre-approved pattern ("Verify Lookup"), not a free-text
    SMS — a plain message containing a login code is routinely rejected
    for compliance. When both `otp_code` and a verify template are
    configured, the provider must call verify/lookup.json (GET, token +
    template params) instead of sms/send.json (POST, free-text message)."""
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/v1/secret-key/verify/lookup.json"
        params = dict(request.url.params)
        assert params["receptor"] == "09121234567"
        assert params["token"] == "123456"
        assert params["template"] == "verify"
        return httpx.Response(
            200,
            json={"return": {"status": 200, "message": "تایید شد"}, "entries": [{"messageid": 555}]},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = KavenegarSmsProvider(
            api_key="secret-key", sender="10001234", verify_template="verify", client=client,
        )
        result = await provider.send(phone="+989121234567", text="کد تایید: 123456", otp_code="123456")
    assert result == SmsSendResult(accepted=True, provider="kavenegar", message_id="555")


@pytest.mark.asyncio
async def test_kavenegar_falls_back_to_plain_send_without_verify_template():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/v1/secret-key/sms/send.json"
        return httpx.Response(200, json={"return": {"status": 200}, "entries": [{"messageid": 1}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = KavenegarSmsProvider(api_key="secret-key", sender="10001234", client=client)
        result = await provider.send(phone="+989121234567", text="test", otp_code="123456")
    assert result.accepted is True
