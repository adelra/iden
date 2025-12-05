from __future__ import annotations

import time
import secrets
from typing import Callable, Final, Optional

from . import utils


# ~22k hosts before 50% chance of initial counter collision
# with a remaining counter range of 9.0e+15 in JavaScript.
INITIAL_COUNT_MAX: Final[int] = 476782367
_default_length = 24
DEFAULT_LENGTH = _default_length
_big_length = 32
MAXIMUM_LENGTH = _big_length


class Cuid2Generator:  # pylint: disable=too-few-public-methods
    def __init__(
        self: Cuid2Generator,
        counter: Callable[[int], Callable[[], int]] = utils.create_counter,
        length: int = _default_length,
        fingerprint: Callable[[], str] = utils.create_fingerprint,
    ) -> None:
        """
        Initializes the Cuid2Generator class for generating CUIDs.

        Parameters
        ----------
        counter : Callable[[int], Callable[[], int]], optional
            A function that creates a counter.
            Defaults to `utils.create_counter`.
        length : int, optional
            The desired length of the CUID. Must be between 2 and `MAXIMUM_LENGTH`.
            Defaults to `DEFAULT_LENGTH`.
        fingerprint : "FingerprintCallable", optional
            A function that generates a machine fingerprint.
            Defaults to `utils.create_fingerprint`.

        Raises
        ------
        ValueError
            If the length is not between 2 and `MAXIMUM_LENGTH`.
        """
        if not (2 <= length <= MAXIMUM_LENGTH):
            msg = f"Length must be between 2 and {MAXIMUM_LENGTH} (inclusive)."
            raise ValueError(msg)

        self._counter: Callable[[], int] = counter(secrets.randbelow(INITIAL_COUNT_MAX))
        self._length: int = length
        self._fingerprint: str = fingerprint()

    def generate(self: Cuid2Generator, length: Optional[int] = None) -> str:
        """
        Generates a CUID string.

        Parameters
        ----------
        length : int, optional
            The desired length of the CUID. If not provided, the length
            specified during initialization is used.

        Returns
        -------
        str
            The generated CUID string.

        Raises
        ------
        ValueError
            If the length is not between 2 and `MAXIMUM_LENGTH`.
        """
        length = length or self._length
        if not (2 <= length <= MAXIMUM_LENGTH):
            msg = f"Length must be between 2 and {MAXIMUM_LENGTH} (inclusive)."
            raise ValueError(msg)

        first_letter: str = utils.create_letter()
        base36_time: str = utils.base36_encode(time.time_ns())
        base36_count: str = utils.base36_encode(self._counter())
        salt: str = utils.create_entropy(length=length)
        hash_input: str = base36_time + salt + base36_count + self._fingerprint

        return first_letter + utils.create_hash(hash_input)[1 : length or self._length]


_cuid2_generator = Cuid2Generator()


def cuid2() -> str:
    """
    Generates a new CUID2.
    This function uses a module-level singleton instance of `Cuid2Generator`.
    Returns
    -------
    str
        A new, unique CUID2 string.
    """
    return _cuid2_generator.generate()
