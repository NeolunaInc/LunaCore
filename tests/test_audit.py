from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.audit.logger import AuditEvent, AuditLogger
from services.audit.storage import AuditStorage


@pytest.fixture
def audit_logger():
    return AuditLogger(secret_key="test-secret-key")


@pytest.fixture
def mock_pool():
    pool = MagicMock()
    conn = AsyncMock()
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=conn)
    cm.__aexit__ = AsyncMock(return_value=None)
    pool.acquire = MagicMock(return_value=cm)
    return pool, conn


@pytest.fixture
def audit_storage(mock_pool):
    pool, conn = mock_pool
    storage = AuditStorage(dsn="postgresql://test")
    storage.pool = pool
    return storage, conn


class TestAuditLogger:
    def test_create_event(self, audit_logger):
        event = audit_logger._create_event(
            event_type="user_action",
            actor="user123",
            resource="project456",
            action="create",
            data={"key": "value"},
        )

        assert event.event_type == "user_action"
        assert event.actor == "user123"
        assert event.resource == "project456"
        assert event.action == "create"
        assert event.data == {"key": "value"}
        assert isinstance(event.timestamp, datetime)
        assert event.signature is not None
        assert len(event.signature) == 64  # SHA256 hex length

    def test_verify_event_valid(self, audit_logger):
        event = audit_logger._create_event(
            event_type="test", actor="test", resource="test", action="test"
        )

        assert audit_logger.verify_event(event) is True

    def test_verify_event_tampered(self, audit_logger):
        event = audit_logger._create_event(
            event_type="test", actor="test", resource="test", action="test"
        )

        # Tamper with the data
        event.data["tampered"] = "value"

        assert audit_logger.verify_event(event) is False

    def test_log_event(self, audit_logger):
        event = audit_logger.log_event(
            event_type="user_login",
            actor="user123",
            resource="session",
            action="start",
            data={"ip": "192.168.1.1"},
        )

        assert isinstance(event, AuditEvent)
        assert event.event_type == "user_login"
        assert event.actor == "user123"


class TestAuditStorage:
    @pytest.mark.asyncio
    async def test_store_event(self, audit_storage):
        storage, conn = audit_storage
        conn.fetchval = AsyncMock(return_value=1)

        event = AuditEvent(
            timestamp=datetime.utcnow(),
            correlation_id="corr-123",
            event_type="test",
            actor="test",
            resource="test",
            action="test",
            data={},
            signature="test-signature",
        )

        result = await storage.store_event(event)

        assert result == 1
        conn.fetchval.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_events_by_correlation_id(self, audit_storage):
        storage, conn = audit_storage
        mock_row = {
            "id": 1,
            "timestamp": datetime.utcnow(),
            "correlation_id": "corr-123",
            "event_type": "test",
            "actor": "test",
            "resource": "test",
            "action": "test",
            "data": '{"key": "value"}',
            "signature": "test-sig",
            "created_at": datetime.utcnow(),
        }
        conn.fetch = AsyncMock(return_value=[mock_row])

        events = await storage.get_events_by_correlation_id("corr-123")

        assert len(events) == 1
        assert events[0]["correlation_id"] == "corr-123"
        conn.fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_events_by_time_range(self, audit_storage):
        storage, conn = audit_storage
        mock_row = {
            "id": 1,
            "timestamp": datetime.utcnow(),
            "correlation_id": "corr-123",
            "event_type": "test",
            "actor": "test",
            "resource": "test",
            "action": "test",
            "data": '{"key": "value"}',
            "signature": "test-sig",
            "created_at": datetime.utcnow(),
        }
        conn.fetch = AsyncMock(return_value=[mock_row])

        start_time = datetime.utcnow() - timedelta(hours=1)
        end_time = datetime.utcnow() + timedelta(hours=1)

        events = await storage.get_events_by_time_range(start_time, end_time)

        assert len(events) == 1
        conn.fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_event_count(self, audit_storage):
        storage, conn = audit_storage
        conn.fetchval = AsyncMock(return_value=42)

        count = await storage.get_event_count()

        assert count == 42
        conn.fetchval.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect(self):
        storage = AuditStorage(dsn="postgresql://test")

        with patch(
            "services.audit.storage.asyncpg.create_pool", new_callable=AsyncMock
        ) as mock_create_pool:
            mock_pool = MagicMock()
            mock_create_pool.return_value = mock_pool

            await storage.connect()

            assert storage.pool == mock_pool
            mock_create_pool.assert_called_once_with("postgresql://test")
