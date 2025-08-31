import asyncio
import uuid

import pytest

from core.telemetry import (
    generate_correlation_id,
    get_correlation_id,
    metrics_collector,
    set_correlation_id,
    trace_span,
)


def test_generate_correlation_id():
    cid = generate_correlation_id()
    assert isinstance(cid, str)
    assert len(cid) == 36  # UUID4 length
    # Check it's a valid UUID
    uuid.UUID(cid)


def test_get_correlation_id_without_setting():
    # Should generate one if not set
    cid = get_correlation_id()
    assert isinstance(cid, str)
    assert len(cid) == 36


def test_set_and_get_correlation_id():
    test_cid = "test-correlation-id"
    set_correlation_id(test_cid)
    assert get_correlation_id() == test_cid


def test_metrics_collector():
    # Clear metrics
    metrics_collector.metrics.clear()

    # Test increment
    metrics_collector.increment("test_counter")
    assert metrics_collector.get_metrics()["test_counter"] == 1.0

    metrics_collector.increment("test_counter", 2.0)
    assert metrics_collector.get_metrics()["test_counter"] == 3.0

    # Test gauge
    metrics_collector.gauge("test_gauge", 42.0)
    assert metrics_collector.get_metrics()["test_gauge"] == 42.0

    # Test timing
    metrics_collector.timing("test_timing", 1.5)
    assert metrics_collector.get_metrics()["test_timing"] == 1.5


@pytest.mark.asyncio
async def test_trace_span(capfd):
    # Clear metrics
    metrics_collector.metrics.clear()

    set_correlation_id("test-cid")

    async def dummy_task():
        await asyncio.sleep(0.01)

    with trace_span("test_span"):
        await dummy_task()

    # Check output
    captured = capfd.readouterr()
    assert "Start span 'test_span' correlation_id=test-cid" in captured.out
    assert "End span 'test_span' duration=" in captured.out
    assert "correlation_id=test-cid" in captured.out

    # Check metrics
    metrics = metrics_collector.get_metrics()
    assert "span.test_span.duration" in metrics
    assert metrics["span.test_span.duration"] > 0
