import datetime
import hashlib
import os
import threading
import time


# XID constants
TIMESTAMP_BYTES = 4
MACHINE_ID_BYTES = 3
PROCESS_ID_BYTES = 2
COUNTER_BYTES = 3
XID_BYTES = TIMESTAMP_BYTES + MACHINE_ID_BYTES + PROCESS_ID_BYTES + COUNTER_BYTES


def _generate_machine_id() -> bytes:
    """
    Generates a 3-byte machine identifier based on hostname.

    Returns:
        A 3-byte machine identifier.
    """
    hostname = os.uname().nodename
    hash_bytes = hashlib.sha256(hostname.encode()).digest()
    return hash_bytes[:MACHINE_ID_BYTES]


def _generate_process_id() -> bytes:
    """
    Generates a 2-byte process identifier from the current process ID.

    Returns:
        A 2-byte process identifier.
    """
    pid = os.getpid() % (1 << (PROCESS_ID_BYTES * 8))
    return pid.to_bytes(PROCESS_ID_BYTES, "big")


class Xid:
    """Represents a globally unique, time-sortable XID."""

    def __init__(
        self, timestamp: int, machine_id: bytes, process_id: bytes, counter: int
    ):
        """
        Initializes a new Xid object.

        Args:
            timestamp: Unix timestamp in seconds.
            machine_id: 3-byte machine identifier.
            process_id: 2-byte process identifier.
            counter: 3-byte counter value.

        Raises:
            ValueError: If any component has invalid length or value.
        """
        if not isinstance(timestamp, int) or timestamp < 0:
            raise ValueError("Timestamp must be a non-negative integer.")
        if not isinstance(machine_id, bytes) or len(machine_id) != MACHINE_ID_BYTES:
            raise ValueError(f"Machine ID must be {MACHINE_ID_BYTES} bytes.")
        if not isinstance(process_id, bytes) or len(process_id) != PROCESS_ID_BYTES:
            raise ValueError(f"Process ID must be {PROCESS_ID_BYTES} bytes.")
        if (
            not isinstance(counter, int)
            or counter < 0
            or counter >= (1 << (COUNTER_BYTES * 8))
        ):
            raise ValueError(
                f"Counter must be between 0 and {(1 << (COUNTER_BYTES * 8)) - 1}."
            )

        self.timestamp = timestamp
        self.machine_id = machine_id
        self.process_id = process_id
        self.counter = counter

    def __str__(self) -> str:
        """Returns the 24-character hexadecimal string representation of the XID."""
        return self.to_bytes().hex()

    def to_bytes(self) -> bytes:
        """Returns the 12-byte representation of the XID."""
        timestamp_bytes = self.timestamp.to_bytes(TIMESTAMP_BYTES, "big")
        counter_bytes = self.counter.to_bytes(COUNTER_BYTES, "big")
        return timestamp_bytes + self.machine_id + self.process_id + counter_bytes

    def __repr__(self) -> str:
        """Returns a developer-friendly representation of the XID."""
        return (
            f"Xid(timestamp={self.timestamp}, "
            f"machine_id={self.machine_id.hex()}, "
            f"process_id={self.process_id.hex()}, "
            f"counter={self.counter})"
        )

    def __lt__(self, other):
        """Compares this XID with another for sorting."""
        if not isinstance(other, Xid):
            return NotImplemented
        return self.to_bytes() < other.to_bytes()

    def __eq__(self, other):
        """Checks if this XID is equal to another."""
        if not isinstance(other, Xid):
            return NotImplemented
        return self.to_bytes() == other.to_bytes()

    def __le__(self, other):
        """Checks if this XID is less than or equal to another."""
        if not isinstance(other, Xid):
            return NotImplemented
        return self.to_bytes() <= other.to_bytes()

    def get_timestamp(self) -> datetime.datetime:
        """
        Returns the timestamp as a UTC datetime object.

        Returns:
            The timestamp as a timezone-aware datetime in UTC.
        """
        return datetime.datetime.fromtimestamp(self.timestamp, tz=datetime.timezone.utc)

    @classmethod
    def from_string(cls, xid_str: str) -> "Xid":
        """
        Parses a hexadecimal string back into an Xid object.

        Args:
            xid_str: A 24-character hexadecimal string.

        Returns:
            An Xid object.

        Raises:
            ValueError: If the string is not a valid XID format.
        """
        if not isinstance(xid_str, str) or len(xid_str) != XID_BYTES * 2:
            raise ValueError(
                f"XID string must be {XID_BYTES * 2} hexadecimal characters."
            )

        try:
            xid_bytes = bytes.fromhex(xid_str)
        except ValueError:
            raise ValueError("XID string must contain valid hexadecimal characters.")

        return cls.from_bytes(xid_bytes)

    @classmethod
    def from_bytes(cls, xid_bytes: bytes) -> "Xid":
        """
        Parses bytes into an Xid object.

        Args:
            xid_bytes: 12 bytes representing an XID.

        Returns:
            An Xid object.

        Raises:
            ValueError: If the bytes are not the correct length.
        """
        if len(xid_bytes) != XID_BYTES:
            raise ValueError(f"XID must be {XID_BYTES} bytes.")

        timestamp = int.from_bytes(xid_bytes[:TIMESTAMP_BYTES], "big")
        machine_id = xid_bytes[TIMESTAMP_BYTES : TIMESTAMP_BYTES + MACHINE_ID_BYTES]
        process_id = xid_bytes[
            TIMESTAMP_BYTES
            + MACHINE_ID_BYTES : TIMESTAMP_BYTES
            + MACHINE_ID_BYTES
            + PROCESS_ID_BYTES
        ]
        counter = int.from_bytes(
            xid_bytes[TIMESTAMP_BYTES + MACHINE_ID_BYTES + PROCESS_ID_BYTES :], "big"
        )

        return cls(
            timestamp=timestamp,
            machine_id=machine_id,
            process_id=process_id,
            counter=counter,
        )


class XidGenerator:
    """
    A thread-safe generator for creating globally unique XIDs.

    XIDs are designed to be globally unique and sortable by the time they
    were created. This class provides a simple interface for generating
    XID objects.

    Usage:
        >>> generator = XidGenerator()
        >>> xid = generator.generate()
        >>> print(xid)
    """

    def __init__(self):
        """
        Initializes a new XidGenerator.

        The machine ID and process ID are generated once and reused for all XIDs.
        The counter starts at a random value for better distribution.
        """
        self._machine_id = _generate_machine_id()
        self._process_id = _generate_process_id()
        self._counter = int.from_bytes(os.urandom(COUNTER_BYTES), "big")
        self._counter_max = (1 << (COUNTER_BYTES * 8)) - 1
        self._lock = threading.Lock()

    def generate(self) -> Xid:
        """
        Generates a new XID object.

        The generated XID combines a timestamp, machine ID, process ID, and an
        incrementing counter, ensuring both sortability and uniqueness.

        Returns:
            A new Xid object.

        Example:
            >>> generator = XidGenerator()
            >>> new_xid = generator.generate()
            >>> isinstance(new_xid, Xid)
            True
        """
        with self._lock:
            timestamp = int(time.time())
            counter = self._counter
            self._counter = (self._counter + 1) % (self._counter_max + 1)

        return Xid(
            timestamp=timestamp,
            machine_id=self._machine_id,
            process_id=self._process_id,
            counter=counter,
        )
