import time
import datetime

# Twitter Snowflake's epoch is 2010-11-04T01:42:54.657Z
SNOWFLAKE_EPOCH_DATETIME = datetime.datetime(
    2010, 11, 4, 1, 42, 54, 657000, tzinfo=datetime.timezone.utc
)
SNOWFLAKE_EPOCH = int(
    SNOWFLAKE_EPOCH_DATETIME.timestamp() * 1000
)  # Convert to milliseconds

WORKER_ID_BITS = (
    5  # Number of bits allocated for the worker ID (allows 2^5 = 32 unique workers)
)
DATACENTER_ID_BITS = 5  # Number of bits allocated for the datacenter ID (allows 2^5 = 32 unique datacenters)
SEQUENCE_BITS = 12  # Number of bits allocated for the sequence number (allows 2^12 = 4096 IDs per millisecond)

MAX_WORKER_ID = -1 ^ (-1 << WORKER_ID_BITS)  # Maximum value for the worker ID
MAX_DATACENTER_ID = -1 ^ (
    -1 << DATACENTER_ID_BITS
)  # Maximum value for the datacenter ID

WORKER_ID_SHIFT = SEQUENCE_BITS  # How many bits to shift the worker ID to the left
DATACENTER_ID_SHIFT = (
    SEQUENCE_BITS + WORKER_ID_BITS
)  # How many bits to shift the datacenter ID to the left
TIMESTAMP_SHIFT = (
    SEQUENCE_BITS + WORKER_ID_BITS + DATACENTER_ID_BITS
)  # How many bits to shift the timestamp to the left

SEQUENCE_MASK = -1 ^ (-1 << SEQUENCE_BITS)


class Snowflake:
    """Represents a Snowflake ID."""

    def __init__(
        self, timestamp: int, worker_id: int, datacenter_id: int, sequence: int
    ):
        if not (0 <= worker_id <= MAX_WORKER_ID):
            raise ValueError(f"Worker ID must be between 0 and {MAX_WORKER_ID}")
        if not (0 <= datacenter_id <= MAX_DATACENTER_ID):
            raise ValueError(f"Datacenter ID must be between 0 and {MAX_DATACENTER_ID}")

        self.timestamp = timestamp
        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = sequence

    def __str__(self) -> str:
        """Returns the string representation of the Snowflake ID."""
        snowflake_id = (
            ((self.timestamp - SNOWFLAKE_EPOCH) << TIMESTAMP_SHIFT)
            | (self.datacenter_id << DATACENTER_ID_SHIFT)
            | (self.worker_id << WORKER_ID_SHIFT)
            | self.sequence
        )
        return str(snowflake_id)


class SnowflakeGenerator:
    """A generator for creating Snowflake IDs."""

    def __init__(self, worker_id: int, datacenter_id: int):
        if not (0 <= worker_id <= MAX_WORKER_ID):
            raise ValueError(f"Worker ID must be between 0 and {MAX_WORKER_ID}")
        if not (0 <= datacenter_id <= MAX_DATACENTER_ID):
            raise ValueError(f"Datacenter ID must be between 0 and {MAX_DATACENTER_ID}")

        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = 0
        self.last_timestamp = -1

    def generate(self) -> Snowflake:
        """Generates a new Snowflake ID."""
        timestamp = int(time.time() * 1000)

        if timestamp < self.last_timestamp:
            raise Exception("Clock moved backwards. Refusing to generate id")

        if self.last_timestamp == timestamp:
            self.sequence = (self.sequence + 1) & SEQUENCE_MASK
            if self.sequence == 0:
                # Sequence overflow, wait for next millisecond
                while timestamp <= self.last_timestamp:
                    timestamp = int(time.time() * 1000)
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        return Snowflake(
            timestamp=timestamp,
            worker_id=self.worker_id,
            datacenter_id=self.datacenter_id,
            sequence=self.sequence,
        )
