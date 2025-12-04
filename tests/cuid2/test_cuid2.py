from anyid import cuid2
from anyid.cuid2 import Cuid2Generator, DEFAULT_LENGTH, MAXIMUM_LENGTH
import pytest
import re


def test_cuid2_generation():
    generated_ids = set()
    for _ in range(1000):
        new_id = cuid2()
        assert isinstance(new_id, str)
        assert len(new_id) == DEFAULT_LENGTH
        assert new_id not in generated_ids
        generated_ids.add(new_id)


def test_cuid2_length():
    assert len(cuid2()) == DEFAULT_LENGTH

    cuid_custom = Cuid2Generator(length=10)
    assert len(cuid_custom.generate()) == 10

    cuid_generate_override = Cuid2Generator(length=DEFAULT_LENGTH)
    assert len(cuid_generate_override.generate(length=15)) == 15


def test_cuid2_invalid_length():
    with pytest.raises(
        ValueError,
        match=re.escape(f"Length must be between 2 and {MAXIMUM_LENGTH} (inclusive)."),
    ):
        Cuid2Generator(length=MAXIMUM_LENGTH + 1)

    cuid_instance = Cuid2Generator()
    with pytest.raises(
        ValueError,
        match=re.escape(f"Length must be between 2 and {MAXIMUM_LENGTH} (inclusive)."),
    ):
        cuid_instance.generate(length=MAXIMUM_LENGTH + 1)


def test_cuid2_uniqueness_over_time():
    # This test is more about ensuring the counter and random elements work
    # rather than true cryptographic uniqueness, which is hard to test in unit tests.
    cuid_gen = Cuid2Generator()
    ids = [cuid_gen.generate() for _ in range(100)]
    assert len(set(ids)) == 100


def test_cuid2_starts_with_letter():
    for _ in range(100):
        new_id = cuid2()
        assert new_id[0].isalpha() and new_id[0].islower()
