import uuid as _uuid


class UuidGenerator:
    """
    A generator for creating Version 4 UUIDs (Universally Unique Identifiers).

    This class uses Python's built-in `uuid` module to generate random,
    RFC 4122 compliant UUIDs.

    Usage:
        >>> generator = UuidGenerator()
        >>> new_uuid = generator.generate()
        >>> isinstance(new_uuid, _uuid.UUID)
        True
    """

    def generate(self) -> _uuid.UUID:
        """
        Generates a new, random Version 4 UUID.

        Returns:
            A new UUID object.

        Example:
            >>> import uuid
            >>> generator = UuidGenerator()
            >>> new_uuid = generator.generate()
            >>> new_uuid.version
            4
        """
        return _uuid.uuid4()


_uuid_generator = UuidGenerator()


def uuid() -> _uuid.UUID:
    """
    Generates a new, random Version 4 UUID.

    This function uses a module-level singleton instance of `UuidGenerator`.

    Returns
    -------
    _uuid.UUID
        A new, unique UUID object.
    """
    return _uuid_generator.generate()
