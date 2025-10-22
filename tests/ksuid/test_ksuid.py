import secrets

from iden.ksuid.generator import BASE62_ALPHABET, Ksuid, KsuidGenerator


def test_ksuid_generator():
    """
    Tests that the KsuidGenerator returns a valid KSUID of the correct type.
    """
    generator = KsuidGenerator()
    generated_ksuid = generator.generate()
    assert isinstance(generated_ksuid, Ksuid)


def test_ksuid_string_representation():
    """
    Tests that the string representation of a KSUID is correct.
    """
    generator = KsuidGenerator()
    generated_ksuid = generator.generate()
    ksuid_str = str(generated_ksuid)

    assert len(ksuid_str) == 27
    for char in ksuid_str:
        assert char in BASE62_ALPHABET


def test_ksuid_sorting():
    """
    Tests that KSUIDs are sortable by time and then by payload.
    """
    # Test sorting by timestamp
    payload = secrets.token_bytes(16)
    ksuid1 = Ksuid(timestamp=1000, payload=payload)
    ksuid2 = Ksuid(timestamp=2000, payload=payload)
    assert ksuid1 < ksuid2

    # Test sorting by payload when timestamps are equal
    ksuid3 = Ksuid(timestamp=1000, payload=b"\x00" * 16)
    ksuid4 = Ksuid(timestamp=1000, payload=b"\xff" * 16)
    assert ksuid3 < ksuid4
