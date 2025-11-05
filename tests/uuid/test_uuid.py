import uuid

from iden.uuid import UuidGenerator


def test_uuid_generator():
    """
    Tests that the UuidGenerator returns a valid UUID.
    """
    generator = UuidGenerator()
    generated_uuid = generator.generate()
    assert isinstance(generated_uuid, uuid.UUID)
