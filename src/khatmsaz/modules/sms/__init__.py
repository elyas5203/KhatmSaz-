"""Pluggable SMS delivery boundary.

The application depends on this small interface rather than a vendor SDK.
The default provider is deliberately a no-op until a real SMS vendor and
credentials are configured.
"""

from khatmsaz.modules.sms.provider import KavenegarSmsProvider, NoopSmsProvider, SmsProvider, build_provider

__all__ = ["KavenegarSmsProvider", "NoopSmsProvider", "SmsProvider", "build_provider"]
