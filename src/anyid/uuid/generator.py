import uuid


class UuidGenerator:
    """
    A generator for creating Version 4 UUIDs (Universally Unique Identifiers).

    This class uses Python's built-in `uuid` module to generate random,
    RFC 4122 compliant UUIDs.

    Usage:
        >>> generator = UuidGenerator()
        >>> new_uuid = generator.generate()
        >>> isinstance(new_uuid, uuid.UUID)
        True
    """

    def generate(self) -> uuid.UUID:
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
        return uuid.uuid4()
