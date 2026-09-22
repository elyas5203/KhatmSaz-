"""Gateway boundary; PSP-specific code must live behind this protocol."""

from dataclasses import dataclass
from typing import Protocol


class GatewayError(Exception):
    """The PSP rejected or could not complete a request."""


@dataclass(frozen=True)
class PaymentRequest:
    authority: str
    payment_url: str


@dataclass(frozen=True)
class PaymentVerification:
    authority: str
    amount_toman: int
    transaction_ref: str


class PaymentGateway(Protocol):
    async def request_payment(
        self, *, amount_toman: int, description: str, callback_url: str,
        client_ref_id: str,
    ) -> PaymentRequest: ...

    async def verify_payment(
        self, *, authority: str, amount_toman: int, transaction_ref: str,
        client_ref_id: str,
    ) -> PaymentVerification: ...
