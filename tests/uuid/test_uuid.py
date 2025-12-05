import uuid as _uuid

import pytest

from anyid.uuid import UuidGenerator, uuid, uuid1, uuid3, uuid4, uuid5


def test_uuid_generator():
    """
    Tests that the UuidGenerator returns a valid UUID.
    """
    generator = UuidGenerator()
    generated_uuid = generator.generate()
    assert isinstance(generated_uuid, _uuid.UUID)
    assert generated_uuid.version == 4


def test_uuid_versions():
    """
    Tests that the uuid function returns a valid UUID for each version.
    """
    assert uuid(version=1).version == 1
    assert uuid(version=4).version == 4

    namespace = _uuid.NAMESPACE_DNS
    name = "example.com"
    assert uuid(version=3, namespace=namespace, name=name).version == 3
    assert uuid(version=5, namespace=namespace, name=name).version == 5


def test_uuid_convenience_functions():
    """
    Tests the convenience functions for each UUID version.
    """
    assert uuid1().version == 1
    assert uuid4().version == 4

    namespace = _uuid.NAMESPACE_DNS
    name = "example.com"
    assert uuid3(namespace, name).version == 3
    assert uuid5(namespace, name).version == 5


def test_uuid_collision():
    """
    Tests for UUID collisions.
    """
    generator = UuidGenerator()
    ids = [generator.generate() for _ in range(10000)]
    assert len(ids) == len(set(ids))


def test_name_based_uuids():
    """
    Tests that name-based UUIDs (v3 and v5) are consistent.
    """
    namespace = _uuid.NAMESPACE_DNS
    name = "example.com"
    uuid_v3_1 = uuid3(namespace, name)
    uuid_v3_2 = uuid3(namespace, name)
    assert uuid_v3_1 == uuid_v3_2

    uuid_v5_1 = uuid5(namespace, name)
    uuid_v5_2 = uuid5(namespace, name)
    assert uuid_v5_1 == uuid_v5_2


def test_string_namespace():
    """
    Tests that a string namespace works for v3/v5.
    """
    namespace_uuid = _uuid.NAMESPACE_DNS
    namespace_str = str(namespace_uuid)
    name = "example.com"

    assert uuid3(namespace_str, name) == uuid3(namespace_uuid, name)
    assert uuid5(namespace_str, name) == uuid5(namespace_uuid, name)


def test_invalid_version():
    """
    Tests that an invalid version raises a ValueError.
    """
    with pytest.raises(ValueError, match="Unsupported UUID version"):
        uuid(version=2)


def test_missing_name():
    """
    Tests that a missing name for v3/v5 raises a ValueError.
    """
    with pytest.raises(ValueError, match="name is required"):
        uuid(version=3)

    with pytest.raises(ValueError, match="name is required"):
        uuid(version=5)


def test_missing_namespace():
    """
    Tests that a missing namespace for v3/v5 raises a TypeError.
    """
    name = "example.com"
    with pytest.raises(TypeError):
        uuid3(name=name)

    with pytest.raises(TypeError):
        uuid5(name=name)
