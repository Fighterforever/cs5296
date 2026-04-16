import pytest

from src.codec import decode, encode, hash_code


@pytest.mark.parametrize("n", [0, 1, 61, 62, 1_000, 1 << 32, (1 << 63) - 1])
def test_roundtrip(n):
    assert decode(encode(n)) == n


def test_hash_code_stable():
    a = hash_code("https://example.com/")
    b = hash_code("https://example.com/")
    assert a == b
    assert len(a) == 7


def test_hash_code_differs():
    assert hash_code("https://a") != hash_code("https://b")


def test_decode_rejects_bad():
    with pytest.raises(ValueError):
        decode("not-valid-!")
