import json
from datetime import datetime
from typing import Any

import asyncpg

from services.audit.logger import AuditEvent


class AuditStorage:
    """Append-only audit storage with PostgreSQL."""

    def __init__(self, dsn: str, table_name: str = "audit_events"):
        self.dsn = dsn
        self.table_name = table_name
        self.pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        """Connect to the database and create audit table if needed."""
        self.pool = await asyncpg.create_pool(self.dsn)
        async with self.pool.acquire() as conn:
            await conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    correlation_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    action TEXT NOT NULL,
                    data JSONB,
                    signature TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );

                -- Create index on correlation_id for efficient queries
                CREATE INDEX IF NOT EXISTS idx_audit_correlation_id
                ON {self.table_name} (correlation_id);

                -- Create index on timestamp for time-based queries
                CREATE INDEX IF NOT EXISTS idx_audit_timestamp
                ON {self.table_name} (timestamp);

                -- Create index on event_type for filtering
                CREATE INDEX IF NOT EXISTS idx_audit_event_type
                ON {self.table_name} (event_type);

                -- Prevent any updates or deletes (append-only)
                CREATE OR REPLACE RULE {self.table_name}_no_updates AS
                ON UPDATE TO {self.table_name} DO INSTEAD NOTHING;

                CREATE OR REPLACE RULE {self.table_name}_no_deletes AS
                ON DELETE TO {self.table_name} DO INSTEAD NOTHING;
            """
            )

    async def disconnect(self) -> None:
        """Disconnect from the database."""
        if self.pool:
            await self.pool.close()

    async def store_event(self, event: AuditEvent) -> int:
        """Store an audit event (append-only)."""
        if not self.pool:
            await self.connect()

        assert self.pool is not None
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                f"""
                INSERT INTO {self.table_name}
                (timestamp, correlation_id, event_type, actor, resource,
                 action, data, signature)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
            """,
                event.timestamp,
                event.correlation_id,
                event.event_type,
                event.actor,
                event.resource,
                event.action,
                json.dumps(event.data),
                event.signature,
            )

            return result

    async def get_events_by_correlation_id(
        self, correlation_id: str, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Retrieve audit events by correlation ID."""
        if not self.pool:
            await self.connect()

        assert self.pool is not None
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT id, timestamp, correlation_id, event_type, actor,
                       resource, action, data, signature, created_at
                FROM {self.table_name}
                WHERE correlation_id = $1
                ORDER BY timestamp ASC
                LIMIT $2
            """,
                correlation_id,
                limit,
            )

            return [dict(row) for row in rows]

    async def get_events_by_time_range(
        self,
        start_time: datetime,
        end_time: datetime,
        event_type: str | None = None,
        limit: int = 1000,
    ) -> list[dict[str, Any]]:
        """Retrieve audit events within a time range."""
        if not self.pool:
            await self.connect()

        assert self.pool is not None
        async with self.pool.acquire() as conn:
            if event_type:
                rows = await conn.fetch(
                    f"""
                    SELECT id, timestamp, correlation_id, event_type, actor,
                           resource, action, data, signature, created_at
                    FROM {self.table_name}
                    WHERE timestamp BETWEEN $1 AND $2
                      AND event_type = $3
                    ORDER BY timestamp ASC
                    LIMIT $4
                """,
                    start_time,
                    end_time,
                    event_type,
                    limit,
                )
            else:
                rows = await conn.fetch(
                    f"""
                    SELECT id, timestamp, correlation_id, event_type, actor,
                           resource, action, data, signature, created_at
                    FROM {self.table_name}
                    WHERE timestamp BETWEEN $1 AND $2
                    ORDER BY timestamp ASC
                    LIMIT $4
                """,
                    start_time,
                    end_time,
                    limit,
                )

            return [dict(row) for row in rows]

    async def get_event_count(
        self, correlation_id: str | None = None, event_type: str | None = None
    ) -> int:
        """Get count of audit events with optional filters."""
        if not self.pool:
            await self.connect()

        assert self.pool is not None
        async with self.pool.acquire() as conn:
            if correlation_id and event_type:
                count = await conn.fetchval(
                    f"""
                    SELECT COUNT(*) FROM {self.table_name}
                    WHERE correlation_id = $1 AND event_type = $2
                """,
                    correlation_id,
                    event_type,
                )
            elif correlation_id:
                count = await conn.fetchval(
                    f"""
                    SELECT COUNT(*) FROM {self.table_name}
                    WHERE correlation_id = $1
                """,
                    correlation_id,
                )
            elif event_type:
                count = await conn.fetchval(
                    f"""
                    SELECT COUNT(*) FROM {self.table_name}
                    WHERE event_type = $1
                """,
                    event_type,
                )
            else:
                count = await conn.fetchval(
                    f"""
                    SELECT COUNT(*) FROM {self.table_name}
                """
                )

            return count
