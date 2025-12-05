"""
Tests for the CUID generator.
"""

from anyid.cuid import CuidGenerator, cuid
import secrets


def test_cuid_generator():
    """
    Tests that the CuidGenerator returns a valid CUID basically if it starts with c.
    """
    generator = CuidGenerator()
    generated_cuid = generator.generate()
    assert isinstance(generated_cuid, str)
    assert generated_cuid.startswith("c")


def test_cuid_collision():
    """
    Tests for CUID collisions.
    """
    generator = CuidGenerator()
    ids = [generator.generate() for _ in range(10000)]
    assert len(ids) == len(set(ids))


def test_cuid_length():
    """
    Tests that the CUID has a certain length.
    """
    # CUID length is not fixed, but it should be around 25 characters.
    # This is a loose check.
    generated_cuid = cuid()
    assert len(generated_cuid) > 10
