import uuid as _uuid
import time
import secrets
from typing import Optional, Union


class UuidGenerator:
    """
    A generator for creating UUIDs (Universally Unique Identifiers).

    This class uses Python's built-in `uuid` module to generate
    RFC 4122 compliant UUIDs.

    Usage:
        >>> generator = UuidGenerator()
        >>> new_uuid = generator.generate(version=4)
        >>> isinstance(new_uuid, _uuid.UUID)
        True
    """

    def generate(
        self,
        version: int = 4,
        namespace: Optional[Union[_uuid.UUID, str]] = None,
        name: Optional[str] = None,
    ) -> _uuid.UUID:
        """
        Generates a UUID of the specified version.

        Args:
            version: The UUID version to generate (1, 3, 4, 5, 7, or 8).
            namespace: The namespace for v3/v5 UUIDs. Defaults to `uuid.NAMESPACE_DNS`.
            name: The name for v3/v5 UUIDs. Required for v3/v5.

        Returns:
            A new UUID object.
        """
        if version == 1:
            return _uuid.uuid1()
        if version == 3:
            if name is None:
                raise ValueError("name is required for version 3 UUID")
            ns = namespace or _uuid.NAMESPACE_DNS
            if isinstance(ns, str):
                ns = _uuid.UUID(ns)
            return _uuid.uuid3(ns, name)
        if version == 4:
            return _uuid.uuid4()
        if version == 5:
            if name is None:
                raise ValueError("name is required for version 5 UUID")
            ns = namespace or _uuid.NAMESPACE_DNS
            if isinstance(ns, str):
                ns = _uuid.UUID(ns)
            return _uuid.uuid5(ns, name)
        if version == 7:
            return self._generate_uuid7()
        if version == 8:
            return self._generate_uuid8()
        raise ValueError("Unsupported UUID version")

    def uuid1(self) -> _uuid.UUID:
        """Generates a new Version 1 UUID."""
        return self.generate(version=1)

    def uuid3(self, namespace: Union[_uuid.UUID, str], name: str) -> _uuid.UUID:
        """Generates a new Version 3 UUID."""
        return self.generate(version=3, namespace=namespace, name=name)

    def uuid4(self) -> _uuid.UUID:
        """Generates a new, random Version 4 UUID."""
        return self.generate(version=4)

    def uuid5(self, namespace: Union[_uuid.UUID, str], name: str) -> _uuid.UUID:
        """Generates a new Version 5 UUID."""
        return self.generate(version=5, namespace=namespace, name=name)

    def uuid7(self) -> _uuid.UUID:
        """Generates a new Version 7 UUID (time-ordered)."""
        return self.generate(version=7)

    def uuid8(self) -> _uuid.UUID:
        """Generates a new Version 8 UUID (custom/random)."""
        return self.generate(version=8)

    def _generate_uuid7(self) -> _uuid.UUID:
        """
        Generates a UUIDv7.
        bits 0-47: Unix timestamp in ms
        bits 48-51: version (0111)
        bits 52-63: rand_a
        bits 64-65: variant (10)
        bits 66-127: rand_b
        """
        # Current timestamp in milliseconds
        timestamp_ms = int(time.time() * 1000)

        # Random bits
        rand_a = secrets.randbits(12)
        rand_b = secrets.randbits(62)

        # Construct the 128-bit integer
        # (timestamp_ms << 80) | (7 << 76) | (rand_a << 64) | (2 << 62) | rand_b
        uuid_int = (timestamp_ms & 0xFFFFFFFFFFFF) << 80
        uuid_int |= 7 << 76
        uuid_int |= (rand_a & 0xFFF) << 64
        uuid_int |= 2 << 62
        uuid_int |= rand_b & 0x3FFFFFFFFFFFFFFF

        return _uuid.UUID(int=uuid_int)

    def _generate_uuid8(self) -> _uuid.UUID:
        """
        Generates a UUIDv8.
        This implementation generates 122 bits of random data.
        bits 0-47: custom_a
        bits 48-51: version (1000)
        bits 52-63: custom_b
        bits 64-65: variant (10)
        bits 66-127: custom_c
        """
        custom_a = secrets.randbits(48)
        custom_b = secrets.randbits(12)
        custom_c = secrets.randbits(62)

        uuid_int = (custom_a & 0xFFFFFFFFFFFF) << 80
        uuid_int |= 8 << 76
        uuid_int |= (custom_b & 0xFFF) << 64
        uuid_int |= 2 << 62
        uuid_int |= custom_c & 0x3FFFFFFFFFFFFFFF

        return _uuid.UUID(int=uuid_int)


_uuid_generator = UuidGenerator()


def uuid(
    version: int = 4,
    namespace: Optional[Union[_uuid.UUID, str]] = None,
    name: Optional[str] = None,
) -> _uuid.UUID:
    """
    Generates a UUID of the specified version.

    This function uses a module-level singleton instance of `UuidGenerator`.

    Args:
        version: The UUID version to generate (1, 3, 4, 5, 7, or 8).
        namespace: The namespace for v3/v5 UUIDs. Defaults to `uuid.NAMESPACE_DNS`.
        name: The name for v3/v5 UUIDs. Required for v3/v5.

    Returns:
        A new UUID object.
    """
    return _uuid_generator.generate(version=version, namespace=namespace, name=name)


def uuid1() -> _uuid.UUID:
    """
    Generates a new Version 1 UUID.
    """
    return _uuid_generator.uuid1()


def uuid3(namespace: Union[_uuid.UUID, str], name: str) -> _uuid.UUID:
    """
    Generates a new Version 3 UUID.
    """
    return _uuid_generator.uuid3(namespace, name)


def uuid4() -> _uuid.UUID:
    """
    Generates a new, random Version 4 UUID.
    """
    return _uuid_generator.uuid4()


def uuid5(namespace: Union[_uuid.UUID, str], name: str) -> _uuid.UUID:
    """
    Generates a new Version 5 UUID.
    """
    return _uuid_generator.uuid5(namespace, name)


def uuid7() -> _uuid.UUID:
    """
    Generates a new Version 7 UUID (time-ordered).
    """
    return _uuid_generator.uuid7()


def uuid8() -> _uuid.UUID:
    """
    Generates a new Version 8 UUID (custom/random).
    """
    return _uuid_generator.uuid8()
