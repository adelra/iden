from __future__ import annotations
import string
import secrets
from math import floor
from typing import TYPE_CHECKING, Callable, Final, Optional

try:
    from hashlib import sha3_512 as sha512
except ImportError:
    import warnings

    warnings.warn(
        "sha3_512 is not available, falling back to sha512, this is less secure!",
        UserWarning,
        stacklevel=2,
    )
    from hashlib import sha512  # type: ignore[assignment]
# pylint: disable=ungrouped-imports

BIG_LENGTH: Final = 32

if TYPE_CHECKING:
    from hashlib import _Hash
    from _random import Random


def create_counter(count: int) -> Callable[[], int]:
    """
    Creates a counter function.

    Parameters
    ----------
    count : int
        The initial value of the counter.

    Returns
    -------
    Callable[[], int]
        A function that returns an incremented value each time it is called.
    """

    def counter() -> int:
        nonlocal count
        count += 1
        return count

    return counter


_process_fingerprint: Optional[str] = None


def create_fingerprint(
    random_generator: Random, fingerprint_data: Optional[str] = None
) -> str:
    """
    Creates a machine fingerprint.

    By default, this function returns a consistent, randomly generated
    fingerprint for the current process.

    Parameters
    ----------
    random_generator : "Random"
        A random number generator. Used only if `fingerprint_data` is provided.
    fingerprint_data : str, optional
        Custom data to be used for generating the fingerprint.
        If not provided, a random process-level fingerprint is used.
        Using this is not recommended as it can lead to collisions.

    Returns
    -------
    str
        The generated fingerprint.
    """
    global _process_fingerprint

    if not fingerprint_data:
        if _process_fingerprint is None:
            _process_fingerprint = create_hash(secrets.token_hex(BIG_LENGTH))[
                :BIG_LENGTH
            ]
        return _process_fingerprint

    # The following logic is kept for backward compatibility but is not recommended.
    fingerprint: str = str(fingerprint_data) + create_entropy(
        random_generator, BIG_LENGTH
    )
    return create_hash(fingerprint)[0:BIG_LENGTH]


def create_entropy(random_generator: Random, length: int = 4) -> str:
    """
    Creates a random string for entropy.

    Parameters
    ----------
    random_generator : "Random"
        A random number generator.
    length : int, optional
        The desired length of the entropy string. Defaults to 4.

    Returns
    -------
    str
        A random base36-encoded string of the specified length.

    Raises
    ------
    ValueError
        If `length` is less than 1.
    """
    if length < 1:
        msg = "Cannot create entropy without a length >= 1."
        raise ValueError(msg)

    # TODO: make more readable
    entropy: str = ""
    while len(entropy) < length:
        entropy += base36_encode(floor(random_generator.random() * 36))
    return entropy


def create_hash(data: str) -> str:
    """
    Creates a hash of a string.

    Uses the SHA-512 algorithm (preferring SHA3 if available) and returns
    the result in a base36 encoding.

    Parameters
    ----------
    data : str
        The string to be hashed.

    Returns
    -------
    str
        The base36-encoded hash of the input string.
    """
    hashed_value: _Hash = sha512(data.encode())
    hashed_int: int = int.from_bytes(hashed_value.digest(), byteorder="big")

    # Drop the first character because it will bias the histogram to the left.
    return base36_encode(hashed_int)[1:]


def create_letter(random_generator: Random) -> str:
    """
    Generates a random lowercase letter.

    Parameters
    ----------
    random_generator : "Random"
        A random number generator.

    Returns
    -------
    str
        A single random lowercase letter.
    """
    alphabet: str = string.ascii_lowercase
    return alphabet[floor(random_generator.random() * len(alphabet))]


def base36_encode(number: int) -> str:
    """
    Encodes a positive integer into a base36 string.

    Parameters
    ----------
    number : int
        The integer to be encoded.

    Returns
    -------
    str
        The base36-encoded string representation of the integer.

    Raises
    ------
    ValueError
        If the input number is negative.
    """
    if number < 0:
        msg = "Cannot encode negative integers."
        raise ValueError(msg)

    encoded_string: str = ""
    alphabet: str = string.digits + string.ascii_lowercase
    alphabet_length: int = len(alphabet)

    while number != 0:
        number, mod = divmod(number, alphabet_length)
        encoded_string = alphabet[mod] + encoded_string

    return encoded_string or "0"
