"""UUIDv7 generation.

The original schema uses app-generated UUIDv7 primary keys (time-ordered,
so indexes stay sequential instead of fragmenting like random UUIDv4).
Python's stdlib `uuid` module does not offer uuid7 before 3.14, so a small
compliant implementation lives here.
"""

import os
import time
import uuid


def uuid7() -> uuid.UUID:
    unix_ts_ms = int(time.time() * 1000)
    rand = os.urandom(10)

    ts_bytes = unix_ts_ms.to_bytes(6, "big")
    ver_and_rand_a = bytes([0x70 | (rand[0] & 0x0F), rand[1]])
    var_and_rand_b = bytes([0x80 | (rand[2] & 0x3F)]) + rand[3:10]

    raw = ts_bytes + ver_and_rand_a + var_and_rand_b
    return uuid.UUID(bytes=raw)


def new_id() -> uuid.UUID:
    """Return a fresh id as a `uuid.UUID` — matches every `Mapped[uuid.UUID]`
    primary-key column. Do not stringify: mixing `str` and `UUID` for the
    "same" id compares unequal (`str(u) == u` is False) even though both
    print identically.
    """
    return uuid7()
