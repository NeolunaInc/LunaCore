from __future__ import annotations

import threading

from services.agent_registry.registry import AgentRegistry


class HealthMonitor:
    """Scheduler simple pour exécuter health_tick() périodiquement (thread daemon)."""

    def __init__(self, registry: AgentRegistry, interval_sec: float = 30.0) -> None:
        self._registry = registry
        self._interval = interval_sec
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="HealthMonitor", daemon=True)
        self._thread.start()

    def _loop(self) -> None:
        while not self._stop.is_set():
            self._registry.health_tick()
            self._stop.wait(self._interval)

    def stop(self) -> None:
        if self._thread and self._thread.is_alive():
            self._stop.set()
            self._thread.join(timeout=self._interval * 2)

    # utile pour les tests (sans thread)
    def tick(self) -> None:
        self._registry.health_tick()
