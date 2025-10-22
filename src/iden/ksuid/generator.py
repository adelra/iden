import datetime
import secrets
import time

# KSUID's epoch is 2015-03-09T00:00:00Z
KSUID_EPOCH_DATETIME = datetime.datetime(2015, 3, 9, tzinfo=datetime.timezone.utc)
KSUID_EPOCH = int(KSUID_EPOCH_DATETIME.timestamp())
PAYLOAD_BYTES = 16
TIMESTAMP_BYTES = 4

BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def base62_encode(number: int, length: int) -> str:
    """
    Encodes a large integer into a Base62 string of a fixed length.

    Args:
        number: The integer to encode.
        length: The desired length of the output string. The string will
                be left-padded with the zero-character ('0') if needed.

    Returns:
        The Base62 encoded string.
    """
    if number == 0:
        return BASE62_ALPHABET[0] * length

    encoded = ""
    while number > 0:
        number, remainder = divmod(number, 62)
        encoded = BASE62_ALPHABET[remainder] + encoded

    return encoded.zfill(length)


class Ksuid:
    """Represents a K-Sortable Unique ID."""

    def __init__(self, timestamp: int, payload: bytes):
        """
        Initializes a new Ksuid object from a timestamp and payload.

        Args:
            timestamp: An integer representing the seconds since the KSUID epoch.
            payload: A 16-byte random payload.

        Raises:
            ValueError: If the timestamp is not a non-negative integer or if the
                        payload is not a 16-byte string.
        """
        if not isinstance(timestamp, int) or timestamp < 0:
            raise ValueError("Timestamp must be a non-negative integer.")
        if not isinstance(payload, bytes) or len(payload) != PAYLOAD_BYTES:
            raise ValueError(
                f"Payload must be a byte string of length {PAYLOAD_BYTES}."
            )
        self.timestamp = timestamp
        self.payload = payload

    def __str__(self) -> str:
        """Returns the 27-character string representation of the KSUID."""
        combined_int = int.from_bytes(self.to_bytes(), "big")
        return base62_encode(combined_int, 27)

    def to_bytes(self) -> bytes:
        """Returns the 20-byte representation of the KSUID."""
        return self.timestamp.to_bytes(TIMESTAMP_BYTES, "big") + self.payload

    def __repr__(self) -> str:
        """Returns a developer-friendly representation of the KSUID."""
        return f"Ksuid(timestamp={self.timestamp}, payload={self.payload.hex()})"

    def __lt__(self, other):
        """Compares this KSUID with another for sorting."""
        if not isinstance(other, Ksuid):
            return NotImplemented
        return self.to_bytes() < other.to_bytes()

    def __eq__(self, other):
        """Checks if this KSUID is equal to another."""
        if not isinstance(other, Ksuid):
            return NotImplemented
        return self.to_bytes() == other.to_bytes()


class KsuidGenerator:
    """
    A generator for creating K-Sortable Unique IDs (KSUIDs).

    KSUIDs are designed to be globally unique and sortable by the time they
    were created. This class provides a simple interface for generating
    KSUID objects.

    Usage:
        >>> generator = KsuidGenerator()
        >>> ksuid = generator.generate()
        >>> print(ksuid)
    """

    def generate(self) -> Ksuid:
        """
        Generates a new KSUID object.

        The generated KSUID combines a timestamp with a random payload,
        ensuring both sortability and uniqueness.

        Returns:
            A new KSUID object.

        Example:
            >>> generator = KsuidGenerator()
            >>> new_ksuid = generator.generate()
            >>> isinstance(new_ksuid, Ksuid)
            True
        """
        current_time = int(time.time())
        timestamp = current_time - KSUID_EPOCH
        payload = secrets.token_bytes(PAYLOAD_BYTES)
        return Ksuid(timestamp=timestamp, payload=payload)
