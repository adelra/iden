import uuid as _uuid
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
            version: The UUID version to generate (1, 3, 4, or 5).
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
            return _uuid.uuid3(namespace or _uuid.NAMESPACE_DNS, name)
        if version == 4:
            return _uuid.uuid4()
        if version == 5:
            if name is None:
                raise ValueError("name is required for version 5 UUID")
            return _uuid.uuid5(namespace or _uuid.NAMESPACE_DNS, name)
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
        version: The UUID version to generate (1, 3, 4, or 5).
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
