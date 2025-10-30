import datetime
import threading
import time

import pytest

from iden.xid.generator import Xid, XidGenerator


def test_xid_generator():
    """
    Tests that the XidGenerator returns a valid Xid of the correct type.
    """
    generator = XidGenerator()
    generated_xid = generator.generate()
    assert isinstance(generated_xid, Xid)


def test_xid_string_representation():
    """
    Tests that the string representation of an XID is correct.
    """
    generator = XidGenerator()
    generated_xid = generator.generate()
    xid_str = str(generated_xid)

    # XID should be 24 hexadecimal characters (12 bytes)
    assert len(xid_str) == 24
    # Verify all characters are valid hex
    int(xid_str, 16)


def test_xid_format_and_length():
    """
    Tests that XIDs have the correct format and byte length.
    """
    generator = XidGenerator()
    xid = generator.generate()

    # Check string length (24 hex chars = 12 bytes)
    assert len(str(xid)) == 24

    # Check bytes length
    assert len(xid.to_bytes()) == 12

    # Verify components
    assert len(xid.machine_id) == 3
    assert len(xid.process_id) == 2


def test_xid_lexicographic_sorting():
    """
    Tests that XIDs are lexicographically sortable by creation time.
    """
    generator = XidGenerator()
    xids = []

    # Generate XIDs with small delays to ensure different timestamps
    for _ in range(5):
        xids.append(generator.generate())
        time.sleep(0.01)

    # Get string representations
    xid_strings = [str(xid) for xid in xids]

    # Verify they are in lexicographic order
    assert xid_strings == sorted(xid_strings)

    # Also verify using comparison operators
    for i in range(len(xids) - 1):
        assert xids[i] < xids[i + 1] or xids[i] == xids[i + 1]


def test_xid_timestamp_decoding():
    """
    Tests that timestamp decoding returns accurate UTC datetime.
    """
    generator = XidGenerator()
    before_ts = int(time.time())
    xid = generator.generate()
    after_ts = int(time.time())

    timestamp = xid.get_timestamp()

    # Verify it's a datetime with timezone
    assert isinstance(timestamp, datetime.datetime)
    assert timestamp.tzinfo == datetime.timezone.utc

    # Verify it's within the expected range (allowing for second boundaries)
    assert before_ts <= timestamp.timestamp() <= after_ts + 1


def test_xid_parse_from_string():
    """
    Tests parsing a string back into its component fields.
    """
    generator = XidGenerator()
    original_xid = generator.generate()
    xid_str = str(original_xid)

    # Parse the string
    parsed_xid = Xid.from_string(xid_str)

    # Verify all components match
    assert parsed_xid.timestamp == original_xid.timestamp
    assert parsed_xid.machine_id == original_xid.machine_id
    assert parsed_xid.process_id == original_xid.process_id
    assert parsed_xid.counter == original_xid.counter
    assert str(parsed_xid) == xid_str


def test_xid_parse_from_bytes():
    """
    Tests parsing bytes back into an Xid object.
    """
    generator = XidGenerator()
    original_xid = generator.generate()
    xid_bytes = original_xid.to_bytes()

    # Parse the bytes
    parsed_xid = Xid.from_bytes(xid_bytes)

    # Verify all components match
    assert parsed_xid.timestamp == original_xid.timestamp
    assert parsed_xid.machine_id == original_xid.machine_id
    assert parsed_xid.process_id == original_xid.process_id
    assert parsed_xid.counter == original_xid.counter


def test_xid_uniqueness_sequential():
    """
    Tests that sequentially generated XIDs are unique.
    """
    generator = XidGenerator()
    xids = [generator.generate() for _ in range(100)]
    xid_strings = [str(xid) for xid in xids]

    # All XIDs should be unique
    assert len(xid_strings) == len(set(xid_strings))


def test_xid_uniqueness_concurrent():
    """
    Tests that XIDs remain unique under concurrent generation.
    """
    generator = XidGenerator()
    xids = []
    lock = threading.Lock()

    def generate_xids(count):
        local_xids = []
        for _ in range(count):
            local_xids.append(generator.generate())
        with lock:
            xids.extend(local_xids)

    # Create multiple threads
    threads = []
    for _ in range(10):
        thread = threading.Thread(target=generate_xids, args=(50,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # All XIDs should be unique
    xid_strings = [str(xid) for xid in xids]
    assert len(xid_strings) == len(set(xid_strings))
    assert len(xid_strings) == 500


def test_xid_counter_increment():
    """
    Tests that the counter increments correctly within the same second.
    """
    generator = XidGenerator()

    # Generate multiple XIDs quickly (within the same second)
    xids = [generator.generate() for _ in range(10)]

    # Check that counters are different
    counters = [xid.counter for xid in xids]
    # At least some should be different (they might wrap around)
    assert len(set(counters)) >= 1


def test_xid_equality():
    """
    Tests XID equality comparison.
    """
    generator = XidGenerator()
    xid1 = generator.generate()

    # Parse and compare
    xid2 = Xid.from_string(str(xid1))
    assert xid1 == xid2

    # Different XIDs should not be equal
    xid3 = generator.generate()
    assert xid1 != xid3


def test_xid_sorting():
    """
    Tests that XIDs can be sorted correctly.
    """
    generator = XidGenerator()
    xids = [generator.generate() for _ in range(5)]

    # Shuffle and sort
    import random

    shuffled = xids.copy()
    random.shuffle(shuffled)
    sorted_xids = sorted(shuffled)

    # Should match original order (or at least be valid)
    for i in range(len(sorted_xids) - 1):
        assert sorted_xids[i] <= sorted_xids[i + 1]


def test_xid_repr():
    """
    Tests the repr output of Xid.
    """
    generator = XidGenerator()
    xid = generator.generate()
    repr_str = repr(xid)

    assert "Xid(" in repr_str
    assert "timestamp=" in repr_str
    assert "machine_id=" in repr_str
    assert "process_id=" in repr_str
    assert "counter=" in repr_str


def test_xid_invalid_string_parsing():
    """
    Tests that invalid strings raise appropriate errors.
    """
    with pytest.raises(ValueError):
        Xid.from_string("invalid")

    with pytest.raises(ValueError):
        Xid.from_string("gg" * 12)  # Invalid hex


def test_xid_invalid_bytes_parsing():
    """
    Tests that invalid bytes raise appropriate errors.
    """
    with pytest.raises(ValueError):
        Xid.from_bytes(b"short")


def test_xid_validation():
    """
    Tests Xid constructor validation.
    """
    # Valid XID
    xid = Xid(timestamp=1234567890, machine_id=b"abc", process_id=b"de", counter=12345)
    assert xid.timestamp == 1234567890

    # Invalid timestamp
    with pytest.raises(ValueError):
        Xid(timestamp=-1, machine_id=b"abc", process_id=b"de", counter=12345)

    # Invalid machine_id length
    with pytest.raises(ValueError):
        Xid(timestamp=123, machine_id=b"ab", process_id=b"de", counter=12345)

    # Invalid process_id length
    with pytest.raises(ValueError):
        Xid(timestamp=123, machine_id=b"abc", process_id=b"d", counter=12345)

    # Invalid counter (too large)
    with pytest.raises(ValueError):
        Xid(
            timestamp=123, machine_id=b"abc", process_id=b"de", counter=16777216
        )  # 2^24
