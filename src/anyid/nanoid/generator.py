import secrets


class NanoidGenerator:
    """
    A generator for creating cryptographically secure, URL-friendly unique IDs.

    This implementation uses Python's `secrets` module to ensure that the
    generated IDs are suitable for security-sensitive applications.

    Usage:
        >>> generator = NanoidGenerator()
        >>> nanoid = generator.generate()
        >>> print(len(nanoid))
        21
    """

    def generate(
        self,
        size: int = 21,
        alphabet: str = "_~0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    ) -> str:
        """
        Generates a new NanoID with a custom size and alphabet.

        Args:
            size: The desired length of the ID. Defaults to 21.
            alphabet: The set of characters to use for generating the ID.
                      Defaults to a URL-friendly set.

        Returns:
            A new, unique NanoID string.

        Example:
            >>> generator = NanoidGenerator()
            >>> custom_id = generator.generate(size=10, alphabet="0123456789")
            >>> len(custom_id)
            10
            >>> custom_id.isdigit()
            True
        """
        return "".join(secrets.choice(alphabet) for _ in range(size))
