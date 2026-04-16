"""Base62 codec used to derive short codes from sequential ids or content hashes."""
from __future__ import annotations

import hashlib

_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
_BASE = len(_ALPHABET)


def encode(n: int) -> str:
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return _ALPHABET[0]
    out = []
    while n:
        n, r = divmod(n, _BASE)
        out.append(_ALPHABET[r])
    return "".join(reversed(out))


def decode(s: str) -> int:
    n = 0
    for ch in s:
        idx = _ALPHABET.find(ch)
        if idx < 0:
            raise ValueError(f"invalid char {ch!r}")
        n = n * _BASE + idx
    return n


def hash_code(url: str, length: int = 7) -> str:
    """Deterministic short code from URL — 7 chars of base62-ish from SHA-256."""
    digest = hashlib.sha256(url.encode("utf-8")).digest()
    n = int.from_bytes(digest[:8], "big")
    s = encode(n)
    return s[:length].rjust(length, _ALPHABET[0])
