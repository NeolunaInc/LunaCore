import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.memory.postgres_store import PostgresMemoryStore


@pytest.fixture
def mock_pool():
    pool = MagicMock()
    conn = AsyncMock()
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=conn)
    cm.__aexit__ = AsyncMock(return_value=None)
    pool.acquire = MagicMock(return_value=cm)
    return pool, conn


@pytest.mark.asyncio
async def test_put(mock_pool):
    pool, conn = mock_pool
    conn.fetchval = AsyncMock(return_value=1)
    conn.execute = AsyncMock()

    store = PostgresMemoryStore(dsn="postgresql://test")
    store.pool = pool

    artifact = await store.put("key1", "value1", project_id="project1")

    assert artifact.key == "key1"
    assert artifact.data == "value1"
    conn.fetchval.assert_called_once()
    conn.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get(mock_pool):
    pool, conn = mock_pool
    conn.fetchrow = AsyncMock(
        return_value={
            "id": "test-id",
            "key": "key1",
            "data": "value1",
            "meta": {},
            "tenant_id": "default",
            "project_id": "project1",
            "artifact_type": "data",
            "version": 1,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
        }
    )

    store = PostgresMemoryStore(dsn="postgresql://test")
    store.pool = pool

    result = await store.get("key1", project_id="project1")

    assert result is not None
    assert result.key == "key1"
    assert result.data == "value1"
    conn.fetchrow.assert_called_once()


@pytest.mark.asyncio
async def test_get_not_found(mock_pool):
    pool, conn = mock_pool
    conn.fetchrow = AsyncMock(return_value=None)

    store = PostgresMemoryStore(dsn="postgresql://test")
    store.pool = pool

    result = await store.get("key1", project_id="project1")

    assert result is None
    conn.fetchrow.assert_called_once()


@pytest.mark.asyncio
async def test_list_versions(mock_pool):
    pool, conn = mock_pool
    conn.fetch = AsyncMock(return_value=[{"version": 1}, {"version": 2}])

    store = PostgresMemoryStore(dsn="postgresql://test")
    store.pool = pool

    result = await store.list_versions("key1", project_id="project1")

    assert result == [1, 2]
    conn.fetch.assert_called_once()


@pytest.mark.asyncio
async def test_connect():
    store = PostgresMemoryStore(dsn="postgresql://test")

    with patch(
        "services.memory.postgres_store.asyncpg.create_pool", new_callable=AsyncMock
    ) as mock_create_pool:
        mock_pool = MagicMock()
        mock_create_pool.return_value = mock_pool

        await store.connect()

        assert store.pool == mock_pool
        mock_create_pool.assert_called_once_with("postgresql://test")
