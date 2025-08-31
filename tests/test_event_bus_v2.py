import asyncio
import os
import tempfile

import pytest

from core.events import BaseEvent
from services.event_bus.dlq import DLQ
from services.event_bus.wal import WAL


def test_wal_append_and_recover():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        log_file = f.name

    try:
        wal = WAL(log_file)

        # Create test events
        event1 = BaseEvent(type="test.event1", data={"key": "value1"})
        event2 = BaseEvent(type="test.event2", data={"key": "value2"})

        # Append events
        wal.append(event1)
        wal.append(event2)

        # Recover events
        recovered = wal.recover()
        assert len(recovered) == 2
        assert recovered[0].type == "test.event1"
        assert recovered[0].data == {"key": "value1"}
        assert recovered[1].type == "test.event2"
        assert recovered[1].data == {"key": "value2"}

    finally:
        os.unlink(log_file)


def test_wal_empty_recover():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        log_file = f.name

    try:
        wal = WAL(log_file)
        recovered = wal.recover()
        assert recovered == []
    finally:
        os.unlink(log_file)


@pytest.mark.asyncio
async def test_dlq_retry_success():
    dlq = DLQ(max_retries=2)

    success_count = 0

    async def handler(event):
        nonlocal success_count
        success_count += 1

    dlq.add_handler(handler)

    event = BaseEvent(type="test.event", data={"test": True})

    # Enqueue failed event
    dlq.enqueue_failed(event, 0)

    # Wait for retry
    await asyncio.sleep(0.5)

    # Should have succeeded
    assert success_count == 1
    assert len(dlq.get_failed_events()) == 0


@pytest.mark.asyncio
async def test_dlq_max_retries():
    dlq = DLQ(max_retries=3)

    fail_count = 0

    async def failing_handler(event):
        nonlocal fail_count
        fail_count += 1
        raise Exception("Simulated failure")

    dlq.add_handler(failing_handler)

    event = BaseEvent(type="test.event", data={"test": True})

    # Enqueue failed event
    dlq.enqueue_failed(event, 0)

    # Wait for retries
    await asyncio.sleep(1.0)

    # Should have failed 3 times (3 retries) and be in DLQ
    assert fail_count == 3
    failed_events = dlq.get_failed_events()
    assert len(failed_events) == 1
    assert failed_events[0][1] == 3  # retry_count


@pytest.mark.asyncio
async def test_dlq_clear():
    dlq = DLQ(max_retries=1)

    async def failing_handler(event):
        raise Exception("Fail")

    dlq.add_handler(failing_handler)

    event = BaseEvent(type="test.event")
    dlq.enqueue_failed(event, 1)  # Already at max retries

    await asyncio.sleep(0.1)

    assert len(dlq.get_failed_events()) == 1

    dlq.clear_dlq()
    assert len(dlq.get_failed_events()) == 0
