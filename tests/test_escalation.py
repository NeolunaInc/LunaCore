import asyncio

import pytest

from orchestrator.escalation_manager import EscalationManager


@pytest.mark.asyncio
async def test_escalation_chain():
    manager = EscalationManager(
        chain=["llama3:8b", "gpt-3.5-turbo", "gpt-4", "human"], backoff=[1, 2, 4], budget=100.0
    )

    # Start at level 0
    assert manager.escalate(0) == "gpt-3.5-turbo"
    assert manager.escalate(1) == "gpt-4"
    assert manager.escalate(2) == "human"
    assert manager.escalate(3) == "human"  # Stay at end


@pytest.mark.asyncio
async def test_backoff_times():
    manager = EscalationManager(
        chain=["llama3:8b", "gpt-3.5-turbo"], backoff=[1, 2, 4], budget=100.0
    )

    assert manager.get_backoff(1) == 1
    assert manager.get_backoff(2) == 2
    assert manager.get_backoff(3) == 4
    assert manager.get_backoff(4) == 4  # Use last for further attempts


@pytest.mark.asyncio
async def test_budget_tracking():
    manager = EscalationManager(chain=["llama3:8b"], backoff=[1], budget=10.0)

    assert manager.can_afford(5.0) is True
    manager.track_cost(3.0)
    assert manager.budget == 7.0
    assert manager.current_cost == 3.0
    assert manager.can_afford(8.0) is False


@pytest.mark.asyncio
async def test_is_at_end():
    manager = EscalationManager(
        chain=["llama3:8b", "gpt-3.5-turbo", "human"], backoff=[1], budget=100.0
    )

    assert manager.is_at_end(0) is False
    assert manager.is_at_end(1) is False
    assert manager.is_at_end(2) is True


@pytest.mark.asyncio
async def test_wait_backoff():
    manager = EscalationManager(chain=["llama3:8b"], backoff=[0.1], budget=100.0)  # Short for test

    start = asyncio.get_event_loop().time()
    await manager.wait_backoff(1)
    end = asyncio.get_event_loop().time()
    assert end - start >= 0.1
