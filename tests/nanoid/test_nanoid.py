"""
Tests for the NanoID generator.
"""

import string

from hypothesis import given, strategies as st

from iden.nanoid import NanoidGenerator


def test_nanoid_generator():
    """
    Tests that the NanoidGenerator returns a valid NanoID.
    """
    generator = NanoidGenerator()
    generated_nanoid = generator.generate()
    assert isinstance(generated_nanoid, str)
    assert len(generated_nanoid) == 21


def test_nanoid_generator_custom_size():
    """
    Tests that the NanoidGenerator returns a NanoID with a custom size.
    """
    generator = NanoidGenerator()
    generated_nanoid = generator.generate(size=10)
    assert isinstance(generated_nanoid, str)
    assert len(generated_nanoid) == 10


def test_nanoid_generator_custom_alphabet():
    """
    Tests that the NanoidGenerator returns a NanoID with a custom alphabet.
    """
    generator = NanoidGenerator()
    alphabet = string.digits
    generated_nanoid = generator.generate(alphabet=alphabet)
    assert isinstance(generated_nanoid, str)
    for char in generated_nanoid:
        assert char in alphabet


@given(
    size=st.integers(min_value=5, max_value=30),
    alphabet=st.text(
        alphabet=string.ascii_letters + string.digits, min_size=10, max_size=60
    ).map("".join),
)
def test_nanoid_properties(size, alphabet):
    """
    Tests properties of the NanoidGenerator using property-based testing.
    """
    generator = NanoidGenerator()
    generated_nanoid = generator.generate(size=size, alphabet=alphabet)
    assert isinstance(generated_nanoid, str)
    assert len(generated_nanoid) == size
    for char in generated_nanoid:
        assert char in alphabet
