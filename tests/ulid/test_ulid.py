import time
from anyid.ulid import ulid, generator
from anyid.ulid.generator import CROCKFORD_ALPHABET
from hypothesis import given, strategies as st


def test_ulid_length():
    """
    Tests that the generated ULID has the correct length.
    """
    assert len(ulid()) == 26


def test_ulid_alphabet():
    """
    Tests that the generated ULID only contains characters from Crockford's Base32 alphabet.
    """
    for _ in range(100):
        generated_ulid = ulid()
        for char in generated_ulid:
            assert char in CROCKFORD_ALPHABET


def test_ulid_sortable():
    """
    Tests that ULIDs generated in succession are lexicographically sortable.

    This test acts as a general check for sortability and is likely to
    generate ULIDs both within the same millisecond and across different
    milliseconds. The more specific same-millisecond case is handled by
    test_ulid_monotonicity.
    """
    ulids = [ulid() for _ in range(100)]
    sorted_ulids = sorted(ulids)
    assert ulids == sorted_ulids


def test_ulid_monotonicity():
    """
    Tests that ULIDs generated in the same millisecond are monotonic.
    """
    gen = generator()

    # Mock time.time() to control the timestamp
    original_time = time.time

    try:
        current_ms = int(original_time() * 1000)

        # First call
        time.time = lambda: current_ms / 1000
        ulid1 = gen.generate()

        # Second call in the same millisecond
        time.time = lambda: current_ms / 1000
        ulid2 = gen.generate()

        assert ulid1 < ulid2

    finally:
        time.time = original_time


def test_ulid_first_char():
    """
    Tests that the first character of a ULID is within the valid range.
    """
    for _ in range(100):
        generated_ulid = ulid()
        assert generated_ulid[0] <= "7"


@given(st.binary(min_size=16, max_size=16))
def test_encode_decode_roundtrip(data):
    """
    Tests that encoding and then decoding a 16-byte string results in the original string.
    """
    gen = generator()
    encoded = gen.encode_base32(data)
    decoded = gen.decode_base32(encoded)
    assert data == decoded


@given(st.lists(st.builds(ulid), min_size=2, max_size=100))
def test_ulid_sortable_property(ulids):
    """
    Tests that a list of generated ULIDs is sortable.
    """
    sorted_ulids = sorted(ulids)
    assert ulids == sorted_ulids


@given(st.builds(ulid))
def test_ulid_first_char_property(generated_ulid):
    """
    Tests that the first character of a ULID is always within the valid range.
    """
    assert generated_ulid[0] <= "7"
