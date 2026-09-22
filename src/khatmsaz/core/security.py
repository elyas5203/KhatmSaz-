"""Opaque token generation/hashing — used by invitations (and later sessions/OTP).

Matches the original project's pattern: the raw token is handed to the user
once and never stored; only its SHA-256 hash lives in the database.
"""

import hashlib
import secrets


def generate_token(n_bytes: int = 24) -> str:
    return secrets.token_urlsafe(n_bytes)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
