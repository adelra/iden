import time
import os
import random
import socket
import threading


class CuidGenerator:
    """
    A generator for creating CUIDs.

    This class implements the original CUID specification for generating
    collision-resistant unique identifiers.

    Attributes
    ----------
    base : int
        The base for encoding (36).
    block_size : int
        The size of each block in the CUID (4).
    discrete_values : int
        The number of discrete values in a block.
    counter : int
        The counter for generating unique IDs.
    lock : threading.Lock
        A lock for thread-safe counter increments.
    fingerprint : str
        A fingerprint of the host machine.
    """

    def __init__(self):
        """
        Initializes the CUID generator.
        """
        self.base = 36
        self.block_size = 4
        self.discrete_values = self.base**self.block_size
        self.counter = random.randint(0, self.discrete_values - 1)
        self.lock = threading.Lock()  # To ensure thread-safe counter increments.
        self.fingerprint = self._get_fingerprint()

    def _pad(self, value: str, size: int) -> str:
        """
        Pads or truncates a string to a specific size.

        Parameters
        ----------
        value : str
            The string to pad or truncate.
        size : int
            The desired size of the string.

        Returns
        -------
        str
            The padded or truncated string.
        """
        if len(value) > size:
            return value[-size:]
        return "0" * (size - len(value)) + value

    def _to_base36(self, n: int) -> str:
        """
        Converts an integer to a base36 string.

        Parameters
        ----------
        n : int
            The integer to convert.

        Returns
        -------
        str
            The base36-encoded string.
        """
        if n == 0:
            return "0"
        chars = "0123456789abcdefghijklmnopqrstuvwxyz"
        result = ""
        while n > 0:
            n, remainder = divmod(n, self.base)
            result = chars[remainder] + result
        return result

    def _get_fingerprint(self) -> str:
        """
        Generates a machine fingerprint.

        The fingerprint is based on the process ID and hostname.

        Returns
        -------
        str
            The machine fingerprint.
        """
        pid = os.getpid()
        hostname = socket.gethostname()

        # Pad PID in base36 to 2 characters
        pid_str = self._to_base36(pid)
        pad_pid = self._pad(pid_str, 2)

        # Compute host sum: start with length + 36, add char codes
        host_sum = len(hostname) + 36
        for char in hostname:
            host_sum += ord(char)

        host_str = self._to_base36(host_sum)
        pad_host = self._pad(host_str, 2)

        return pad_pid + pad_host

    def generate(self) -> str:
        """
        Generates a new CUID string.

        Returns
        -------
        str
            A new, unique CUID string.
        """
        # Increment the counter in a thread-safe way and wrap around if necessary
        with self.lock:
            counter_val = self.counter
            self.counter = (self.counter + 1) % self.discrete_values

        # Get the current time in milliseconds in base36 (no padding)
        timestamp = self._to_base36(int(time.time() * 1000))

        # Pad the counter to block_size
        counter_str = self._pad(self._to_base36(counter_val), self.block_size)

        # Generate two random blocks, each padded to block_size
        random_block1 = self._pad(
            self._to_base36(random.randint(0, self.discrete_values - 1)),
            self.block_size,
        )
        random_block2 = self._pad(
            self._to_base36(random.randint(0, self.discrete_values - 1)),
            self.block_size,
        )

        # Assemble the CUID parts
        parts = [
            "c",  # The CUID prefix
            timestamp,
            counter_str,
            self.fingerprint,
            random_block1,
            random_block2,
        ]
        return "".join(parts)


# Module-level singleton instance of CuidGenerator (lazy, thread-safe initialization)
_cuid_generator = None
_cuid_generator_lock = threading.Lock()


def cuid() -> str:
    """
    Generates a new CUID.

    This function uses a module-level singleton instance of `CuidGenerator`.

    Returns
    -------
    str
        A new, unique CUID string.
    """
    global _cuid_generator
    if _cuid_generator is None:
        with _cuid_generator_lock:
            if _cuid_generator is None:
                _cuid_generator = CuidGenerator()
    return _cuid_generator.generate()
