from __future__ import annotations

import time

from agents.basic import CounterAgent, EchoAgent, PingAgent
from services.agent_registry import HealthMonitor, AgentRegistry


def test_register_unregister_and_list():
    r = AgentRegistry()
    e, p, c = EchoAgent(), PingAgent(), CounterAgent()
    r.register(e)
    r.register(p)
    r.register(c)
    ids = {rec.spec.agent_id for rec in r.list()}
    assert ids == {"echo", "ping", "counter"}

    r.unregister("ping")
    ids2 = {rec.spec.agent_id for rec in r.list()}
    assert ids2 == {"echo", "counter"}

    r.register(p)
    ids3 = {rec.spec.agent_id for rec in r.list()}
    assert ids3 == {"echo", "ping", "counter"}


def test_health_tick_updates_status():
    r = AgentRegistry()
    e, p, c = EchoAgent(), PingAgent(), CounterAgent()
    r.register(e)
    r.register(p)
    r.register(c)
    m = HealthMonitor(r, interval_sec=60.0)
    m.tick()  # déterministe
    for rec in r.list():
        assert rec.status.healthy in {"healthy", "unhealthy"}
        assert rec.status.last_seen is not None
        assert isinstance(rec.status.details, (str, type(None)))


def test_health_monitor_thread_start_stop():
    r = AgentRegistry()
    e = EchoAgent()
    r.register(e)
    m = HealthMonitor(r, interval_sec=0.05)
    m.start()
    time.sleep(0.12)
    m.stop()
    assert r.get("echo").status.details is not None
