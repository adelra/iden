from __future__ import annotations

import time
from math import floor
from secrets import SystemRandom
from typing import TYPE_CHECKING, Callable, Final, Optional, Protocol

from . import utils

if TYPE_CHECKING:
    from _random import Random


class FingerprintCallable(Protocol):  # pylint: disable=too-few-public-methods
    def __call__(self: FingerprintCallable, random_generator: Random) -> str: ...


# ~22k hosts before 50% chance of initial counter collision
# with a remaining counter range of 9.0e+15 in JavaScript.
INITIAL_COUNT_MAX: Final[int] = 476782367
_default_length = 24
DEFAULT_LENGTH = _default_length
_big_length = 32
MAXIMUM_LENGTH = _big_length


class Cuid:  # pylint: disable=too-few-public-methods
    def __init__(
        self: Cuid,
        random_generator: Callable[[], Random] = SystemRandom,
        counter: Callable[[int], Callable[[], int]] = utils.create_counter,
        length: int = _default_length,
        fingerprint: FingerprintCallable = utils.create_fingerprint,
    ) -> None:
        """
        Initializes the Cuid class for generating CUIDs.

        Parameters
        ----------
        random_generator : Callable[[], "Random"], optional
            A function that returns a random number generator.
            Defaults to `secrets.SystemRandom`.
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

        self._random: Random = random_generator()
        self._counter: Callable[[], int] = counter(
            floor(self._random.random() * INITIAL_COUNT_MAX)
        )
        self._length: int = length
        self._fingerprint: str = fingerprint(random_generator=self._random)

    def generate(self: Cuid, length: Optional[int] = None) -> str:
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

        first_letter: str = utils.create_letter(random_generator=self._random)
        base36_time: str = utils.base36_encode(time.time_ns())
        base36_count: str = utils.base36_encode(self._counter())
        salt: str = utils.create_entropy(length=length, random_generator=self._random)
        hash_input: str = base36_time + salt + base36_count + self._fingerprint

        return first_letter + utils.create_hash(hash_input)[1 : length or self._length]


def cuid_wrapper() -> Callable[[], str]:
    """
    Creates a default CUID generator function.

    This function wraps a single `Cuid` instance with default parameters,
    providing a simple, zero-argument function for generating CUIDs.

    Returns
    -------
    Callable[[], str]
        A function that, when called, returns a new CUID string.
    """
    cuid_generator: Cuid = Cuid()

    def cuid() -> str:
        return cuid_generator.generate()

    return cuid
