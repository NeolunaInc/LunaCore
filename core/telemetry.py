import contextvars
import time
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

# Context variable for correlation ID
correlation_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("correlation_id")


def generate_correlation_id() -> str:
    """Generate a new correlation ID."""
    return str(uuid.uuid4())


def get_correlation_id() -> str:
    """Get the current correlation ID, or generate one if not set."""
    try:
        return correlation_id_var.get()
    except LookupError:
        cid = generate_correlation_id()
        correlation_id_var.set(cid)
        return cid


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID in the current context."""
    correlation_id_var.set(correlation_id)


class MetricsCollector:
    """Simple in-memory metrics collector."""

    def __init__(self):
        self.metrics: dict[str, Any] = {}

    def increment(self, name: str, value: float = 1.0) -> None:
        """Increment a counter metric."""
        if name not in self.metrics:
            self.metrics[name] = 0.0
        self.metrics[name] += value

    def gauge(self, name: str, value: float) -> None:
        """Set a gauge metric."""
        self.metrics[name] = value

    def timing(self, name: str, duration: float) -> None:
        """Record a timing metric."""
        self.metrics[name] = duration

    def get_metrics(self) -> dict[str, Any]:
        """Get all metrics."""
        return self.metrics.copy()


# Global metrics collector
metrics_collector = MetricsCollector()


@contextmanager
def trace_span(name: str) -> Generator[None, None, None]:
    """Context manager for tracing spans."""
    start_time = time.time()
    correlation_id = get_correlation_id()
    print(f"[TRACE] Start span '{name}' correlation_id={correlation_id}")
    try:
        yield
    finally:
        duration = time.time() - start_time
        print(f"[TRACE] End span '{name}' duration={duration:.3f}s correlation_id={correlation_id}")
        metrics_collector.timing(f"span.{name}.duration", duration)
