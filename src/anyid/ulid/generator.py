import time
import secrets
import threading

CROCKFORD_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


class ULIDGenerator:
    """
    Generates Universally Unique Lexicographically Sortable Identifiers (ULIDs).

    This class handles the generation of ULIDs, ensuring they are
    lexicographically sortable and unique, even when generated within
    the same millisecond.
    """

    def __init__(self):
        """
        Initializes the ULIDGenerator.

        Sets up the internal state to track the last generated timestamp
        and random bytes for monotonic ULID generation.
        """
        self._last_ms = 0
        self._last_random_bytes = b""
        self._lock = threading.Lock()

    def generate(self) -> str:
        """
        Generates a new ULID.

        The ULID consists of a 48-bit timestamp and an 80-bit random component.
        If multiple ULIDs are generated within the same millisecond, the random
        component is incremented to maintain lexicographical sortability.

        Returns
        -------
        str
            A 26-character Crockford's Base32 encoded ULID string.
        """
        with self._lock:
            ms_time = int(time.time() * 1000)

            if ms_time == self._last_ms:
                last_random_int = int.from_bytes(self._last_random_bytes, "big")

                if last_random_int >= (1 << 80) - 1:
                    # Random part is at its max, wait for the next millisecond
                    while int(time.time() * 1000) == ms_time:
                        time.sleep(0.0001)  # Sleep for 0.1ms

                    ms_time = int(time.time() * 1000)
                    random_bytes = secrets.token_bytes(10)
                else:
                    # Increment the random part
                    new_random_int = last_random_int + 1
                    random_bytes = new_random_int.to_bytes(10, "big")
            else:
                random_bytes = secrets.token_bytes(10)

            self._last_ms = ms_time
            self._last_random_bytes = random_bytes

        timestamp_bytes = ms_time.to_bytes(6, "big")
        ulid_bytes = timestamp_bytes + random_bytes

        return self.encode_base32(ulid_bytes)

    def encode_base32(self, data: bytes) -> str:
        """
        Encodes a 16-byte (128-bit) byte array into a 26-character Crockford's Base32 string.

        Parameters
        ----------
        data : bytes
            The 16-byte (128-bit) data to encode.

        Returns
        -------
        str
            The 26-character Crockford's Base32 encoded string.

        Raises
        ------
        ValueError
            If the input data is not 16 bytes long.
        """
        if len(data) != 16:
            raise ValueError("Data must be 16 bytes long")

        num = int.from_bytes(data, "big")
        encoded = ""
        for _ in range(26):
            num, remainder = divmod(num, 32)
            encoded = CROCKFORD_ALPHABET[remainder] + encoded
        return encoded

    def decode_base32(self, encoded: str) -> bytes:
        """
        Decodes a 26-character Crockford's Base32 string into a 16-byte (128-bit) byte array.

        Parameters
        ----------
        encoded : str
            The 26-character Crockford's Base32 encoded string.

        Returns
        -------
        bytes
            The 16-byte (128-bit) decoded data.

        Raises
        ------
        ValueError
            If the input string is not 26 characters long, contains invalid characters,
            or represents a value larger than 128 bits.
        """
        if len(encoded) != 26:
            raise ValueError("ULID string must be 26 characters long")

        num = 0
        for char in encoded:
            try:
                value = CROCKFORD_ALPHABET.index(char.upper())
                num = num * 32 + value
            except ValueError:
                raise ValueError(f"Invalid character '{char}' in ULID string")

        # Check if the number is too large for 128 bits
        if num >= (1 << 128):
            raise ValueError("Invalid ULID string: larger than 128 bits")

        return num.to_bytes(16, "big")


_generator = ULIDGenerator()


def ulid() -> str:
    """
    Generates a new ULID using the module-level ULIDGenerator instance.

    Returns
    -------
    str
        A 26-character Crockford's Base32 encoded ULID string.
    """
    return _generator.generate()
