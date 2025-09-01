import json
from collections.abc import Callable
from typing import Any

import asyncpg

from core.artifacts import Artifact
from services.memory.interface import ProjectMemory


class PostgresMemoryStore(ProjectMemory):
    """PostgreSQL-based memory store for artifacts."""

    def __init__(self, dsn: str, acl_check: Callable | None = None, table_name: str = "artifacts"):
        super().__init__(acl_check)
        self.dsn = dsn
        self.table_name = table_name
        self.pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        """Connect to the database and create table if needed."""
        self.pool = await asyncpg.create_pool(self.dsn)
        async with self.pool.acquire() as conn:
            await conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id TEXT PRIMARY KEY,
                    key TEXT NOT NULL,
                    data TEXT,
                    meta JSONB,
                    tenant_id TEXT DEFAULT 'default',
                    project_id TEXT DEFAULT 'default',
                    artifact_type TEXT DEFAULT 'data',
                    version INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS idx_key_version ON {self.table_name} (key, version);
            """
            )

    async def disconnect(self) -> None:
        """Disconnect from the database."""
        if self.pool:
            await self.pool.close()

    async def put(
        self,
        key: str,
        data: str | bytes,
        meta: dict[str, Any] | None = None,
        tenant_id: str = "default",
        project_id: str = "default",
        artifact_type: str = "data",
    ) -> Artifact:
        """Store an artifact."""
        if not self.pool:
            await self.connect()

        # Get next version
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                f"""
                SELECT COALESCE(MAX(version), 0) + 1
                FROM {self.table_name}
                WHERE key = $1 AND tenant_id = $2 AND project_id = $3
            """,
                key,
                tenant_id,
                project_id,
            )

            version = result or 1

            artifact = Artifact(
                key=key,
                data=data,
                meta=meta or {},
                tenant_id=tenant_id,
                project_id=project_id,
                artifact_type=artifact_type,
                version=version,
            )

            await conn.execute(
                f"""
                INSERT INTO {self.table_name}
                (id, key, data, meta, tenant_id, project_id, artifact_type,
                 version, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ON CONFLICT (id) DO UPDATE SET
                    data = EXCLUDED.data,
                    meta = EXCLUDED.meta,
                    updated_at = EXCLUDED.updated_at
            """,
                artifact.id,
                key,
                str(data),
                json.dumps(meta or {}),
                tenant_id,
                project_id,
                artifact_type,
                version,
                artifact.created_at,
                artifact.updated_at,
            )

            return artifact

    async def get(
        self,
        key: str,
        version: int | None = None,
        tenant_id: str = "default",
        project_id: str = "default",
    ) -> Artifact | None:
        """Retrieve an artifact."""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            if version is None:
                row = await conn.fetchrow(
                    f"""
                    SELECT id, key, data, meta, tenant_id, project_id,
                           artifact_type, version, created_at, updated_at
                    FROM {self.table_name}
                    WHERE key = $1 AND tenant_id = $2 AND project_id = $3
                    ORDER BY version DESC
                    LIMIT 1
                """,
                    key,
                    tenant_id,
                    project_id,
                )
            else:
                row = await conn.fetchrow(
                    f"""
                    SELECT id, key, data, meta, tenant_id, project_id,
                           artifact_type, version, created_at, updated_at
                    FROM {self.table_name}
                    WHERE key = $1 AND version = $2 AND tenant_id = $3 AND project_id = $4
                """,
                    key,
                    version,
                    tenant_id,
                    project_id,
                )

            if row:
                return Artifact(
                    id=row["id"],
                    key=row["key"],
                    data=row["data"],
                    meta=row["meta"] or {},
                    tenant_id=row["tenant_id"],
                    project_id=row["project_id"],
                    artifact_type=row["artifact_type"],
                    version=row["version"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
            return None

    async def list_versions(
        self,
        key: str,
        tenant_id: str = "default",
        project_id: str = "default",
    ) -> list[int]:
        """List all versions for a key."""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT version
                FROM {self.table_name}
                WHERE key = $1 AND tenant_id = $2 AND project_id = $3
                ORDER BY version
            """,
                key,
                tenant_id,
                project_id,
            )

            return [row["version"] for row in rows]
