import pytest
from anyid.snowflake.generator import (
    SnowflakeIdGenerator,
    Snowflake,
    MAX_WORKER_ID,
    MAX_DATACENTER_ID,
    SEQUENCE_MASK,
)
import time
from unittest.mock import patch
from anyid.snowflake import generator
from anyid.snowflake import snowflake, setup_snowflake_id_generator


@pytest.fixture(autouse=True)
def reset_snowflake_generator():
    """Ensures the snowflake generator is reset before each test."""
    with patch.object(generator, "_snowflake_generator", None):
        yield


def test_snowflake_uninitialized_raises_error():
    """
    Tests that calling snowflake() before setup raises a RuntimeError.
    """
    with pytest.raises(RuntimeError, match="Snowflake generator is not initialized"):
        snowflake()


def test_snowflake_generation_after_setup():
    """
    Tests that snowflake() generates an ID after setup.
    """
    setup_snowflake_id_generator(worker_id=1, datacenter_id=1)
    generated_snowflake = snowflake()
    assert isinstance(generated_snowflake, Snowflake)
    assert generated_snowflake.worker_id == 1
    assert generated_snowflake.datacenter_id == 1


def test_snowflake_uniqueness_with_setup():
    """
    Tests that snowflake() generates unique IDs after setup.
    """
    setup_snowflake_id_generator(worker_id=2, datacenter_id=3)
    id1 = snowflake()
    id2 = snowflake()
    assert id1 != id2
    assert str(id1) != str(id2)


def test_snowflake_generator():
    """
    Tests that the SnowflakeIdGenerator returns a valid Snowflake ID of the correct type.
    """
    generator = SnowflakeIdGenerator(worker_id=1, datacenter_id=1)
    generated_snowflake = generator.generate()
    assert isinstance(generated_snowflake, Snowflake)


def test_snowflake_uniqueness():
    """
    Tests that the generated Snowflake IDs are unique.
    """
    generator = SnowflakeIdGenerator(worker_id=1, datacenter_id=1)
    id1 = generator.generate()
    id2 = generator.generate()
    assert id1 != id2


def test_snowflake_worker_id_validation():
    """
    Tests that SnowflakeIdGenerator raises ValueError for invalid worker_id.
    """
    with pytest.raises(
        ValueError, match=f"Worker ID must be between 0 and {MAX_WORKER_ID}"
    ):
        SnowflakeIdGenerator(worker_id=MAX_WORKER_ID + 1, datacenter_id=1)
    with pytest.raises(
        ValueError, match=f"Worker ID must be between 0 and {MAX_WORKER_ID}"
    ):
        SnowflakeIdGenerator(worker_id=-1, datacenter_id=1)


def test_snowflake_datacenter_id_validation():
    """
    Tests that SnowflakeIdGenerator raises ValueError for invalid datacenter_id.
    """
    with pytest.raises(
        ValueError, match=f"Datacenter ID must be between 0 and {MAX_DATACENTER_ID}"
    ):
        SnowflakeIdGenerator(worker_id=1, datacenter_id=MAX_DATACENTER_ID + 1)
    with pytest.raises(
        ValueError, match=f"Datacenter ID must be between 0 and {MAX_DATACENTER_ID}"
    ):
        SnowflakeIdGenerator(worker_id=1, datacenter_id=-1)


def test_snowflake_clock_backwards():
    """
    Tests that SnowflakeIdGenerator raises an exception when clock moves backwards.
    """
    generator = SnowflakeIdGenerator(worker_id=1, datacenter_id=1)
    # Generate one ID
    generator.generate()
    # Manually set last_timestamp to a future value to simulate clock moving backwards
    generator.last_timestamp = int(time.time() * 1000) + 1000
    with pytest.raises(
        Exception, match="Clock moved backwards. Refusing to generate id"
    ):
        generator.generate()


def test_snowflake_sequence_overflow():
    """
    Tests that SnowflakeIdGenerator handles sequence overflow correctly.
    """
    generator = SnowflakeIdGenerator(worker_id=1, datacenter_id=1)

    # Mock time.time() to control the timestamp
    with patch("time.time") as mock_time:
        # Set initial fixed time
        fixed_current_time_ms = 1678886400000  # A fixed timestamp in milliseconds
        mock_time.return_value = fixed_current_time_ms / 1000.0

        # Generate SEQUENCE_MASK IDs. After these calls, generator.sequence should be SEQUENCE_MASK - 1.
        for _ in range(SEQUENCE_MASK):
            generator.generate()
        assert generator.sequence == SEQUENCE_MASK - 1

        # Generate one more ID. This will make generator.sequence become SEQUENCE_MASK.
        generator.generate()
        assert generator.sequence == SEQUENCE_MASK

        # Generate one more ID. This will cause the sequence to overflow, and generator.sequence should become 0.
        # The while loop should be triggered, and mock_time needs to be advanced to simulate the next millisecond.
        mock_time.return_value = (fixed_current_time_ms + 1) / 1000.0
        snowflake_id = generator.generate()

        # After overflow, the sequence should be 0 and the generator should have waited for the next millisecond
        assert generator.sequence == 0
        assert generator.last_timestamp == fixed_current_time_ms + 1
        assert isinstance(snowflake_id, Snowflake)


def test_snowflake_class_worker_id_validation():
    """
    Tests that Snowflake class raises ValueError for invalid worker_id.
    """
    with pytest.raises(
        ValueError, match=f"Worker ID must be between 0 and {MAX_WORKER_ID}"
    ):
        Snowflake(timestamp=1, worker_id=MAX_WORKER_ID + 1, datacenter_id=1, sequence=0)
    with pytest.raises(
        ValueError, match=f"Worker ID must be between 0 and {MAX_WORKER_ID}"
    ):
        Snowflake(timestamp=1, worker_id=-1, datacenter_id=1, sequence=0)


def test_snowflake_class_datacenter_id_validation():
    """
    Tests that Snowflake class raises ValueError for invalid datacenter_id.
    """
    with pytest.raises(
        ValueError, match=f"Datacenter ID must be between 0 and {MAX_DATACENTER_ID}"
    ):
        Snowflake(
            timestamp=1, worker_id=1, datacenter_id=MAX_DATACENTER_ID + 1, sequence=0
        )
    with pytest.raises(
        ValueError, match=f"Datacenter ID must be between 0 and {MAX_DATACENTER_ID}"
    ):
        Snowflake(timestamp=1, worker_id=1, datacenter_id=-1, sequence=0)
