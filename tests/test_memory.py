import asyncio
import time
from unittest.mock import Mock

import pytest

from services.memory.file_store import FileProjectMemory
from services.memory.interface import ProjectMemory
from services.memory.mem_inmem import InMemProjectMemory


class TestProjectMemory:
    """Base test class for ProjectMemory implementations."""

    @pytest.fixture
    def acl_check(self):
        """Mock ACL check that allows everything by default."""
        return Mock(return_value=True)

    @pytest.fixture
    def memory_backend(self, acl_check) -> ProjectMemory:
        """Override in subclasses."""
        raise NotImplementedError


class TestInMemProjectMemory(TestProjectMemory):
    """Test InMemProjectMemory implementation."""

    @pytest.fixture
    def memory_backend(self, acl_check) -> ProjectMemory:
        return InMemProjectMemory(acl_check=acl_check)

    @pytest.mark.asyncio
    async def test_put_and_get_basic(self, memory_backend):
        """Test basic put and get operations."""
        # Put an artifact
        artifact = await memory_backend.put(
            key="test_key", data="test data", meta={"type": "string"}, artifact_type="text"
        )

        assert artifact.key == "test_key"
        assert artifact.data == "test data"
        assert artifact.version == 1
        assert artifact.meta["type"] == "string"
        assert artifact.type == "text"

        # Get the artifact
        retrieved = await memory_backend.get("test_key")
        assert retrieved is not None
        assert retrieved.key == "test_key"
        assert retrieved.data == "test data"
        assert retrieved.version == 1

    @pytest.mark.asyncio
    async def test_versioning(self, memory_backend):
        """Test versioning functionality."""
        # Put multiple versions
        await memory_backend.put("versioned_key", "v1", meta={"version": "1"})
        await memory_backend.put("versioned_key", "v2", meta={"version": "2"})
        await memory_backend.put("versioned_key", "v3", meta={"version": "3"})

        # Get latest
        latest = await memory_backend.get("versioned_key")
        assert latest is not None
        assert latest.data == "v3"
        assert latest.version == 3

        # Get specific version
        v2 = await memory_backend.get("versioned_key", version=2)
        assert v2 is not None
        assert v2.data == "v2"
        assert v2.version == 2

        # List versions
        versions = await memory_backend.list_versions("versioned_key")
        assert versions == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_list_versions_empty(self, memory_backend):
        """Test listing versions for non-existent key."""
        versions = await memory_backend.list_versions("nonexistent")
        assert versions == []

    @pytest.mark.asyncio
    async def test_delete_specific_version(self, memory_backend):
        """Test deleting a specific version."""
        await memory_backend.put("delete_key", "v1")
        await memory_backend.put("delete_key", "v2")
        await memory_backend.put("delete_key", "v3")

        # Delete version 2
        result = await memory_backend.delete("delete_key", version=2)
        assert result is True

        # Version 2 should be gone
        v2 = await memory_backend.get("delete_key", version=2)
        assert v2 is None

        # Other versions should remain
        v1 = await memory_backend.get("delete_key", version=1)
        assert v1 is not None
        v3 = await memory_backend.get("delete_key", version=3)
        assert v3 is not None

        # List should not include deleted version
        versions = await memory_backend.list_versions("delete_key")
        assert versions == [1, 3]

    @pytest.mark.asyncio
    async def test_delete_all_versions(self, memory_backend):
        """Test deleting all versions of a key."""
        await memory_backend.put("delete_all_key", "v1")
        await memory_backend.put("delete_all_key", "v2")

        # Delete all
        result = await memory_backend.delete("delete_all_key")
        assert result is True

        # Key should be gone
        retrieved = await memory_backend.get("delete_all_key")
        assert retrieved is None

        versions = await memory_backend.list_versions("delete_all_key")
        assert versions == []

    @pytest.mark.asyncio
    async def test_acl_deny_write(self, memory_backend, acl_check):
        """Test ACL denial for write operations."""
        acl_check.return_value = False

        with pytest.raises(PermissionError, match="Access denied"):
            await memory_backend.put("denied_key", "data")

    @pytest.mark.asyncio
    async def test_acl_deny_read(self, memory_backend, acl_check):
        """Test ACL denial for read operations."""
        # First put with allow
        acl_check.return_value = True
        await memory_backend.put("read_denied_key", "data")

        # Then deny read
        acl_check.return_value = False

        with pytest.raises(PermissionError, match="Access denied"):
            await memory_backend.get("read_denied_key")

    @pytest.mark.asyncio
    async def test_bytes_data(self, memory_backend):
        """Test storing and retrieving bytes data."""
        binary_data = b"\x00\x01\x02\x03\xff"

        await memory_backend.put(key="binary_key", data=binary_data, artifact_type="binary")

        retrieved = await memory_backend.get("binary_key")
        assert retrieved is not None
        assert retrieved.data == binary_data
        assert isinstance(retrieved.data, bytes)

    @pytest.mark.asyncio
    async def test_tenant_project_isolation(self, memory_backend):
        """Test that tenants and projects are isolated."""
        # Put in different tenants/projects
        await memory_backend.put(
            "shared_key", "tenant1_data", tenant_id="tenant1", project_id="proj1"
        )
        await memory_backend.put(
            "shared_key", "tenant2_data", tenant_id="tenant2", project_id="proj1"
        )

        # Get from tenant1
        t1_data = await memory_backend.get("shared_key", tenant_id="tenant1", project_id="proj1")
        assert t1_data is not None
        assert t1_data.data == "tenant1_data"

        # Get from tenant2
        t2_data = await memory_backend.get("shared_key", tenant_id="tenant2", project_id="proj1")
        assert t2_data is not None
        assert t2_data.data == "tenant2_data"

        # Different projects
        await memory_backend.put(
            "shared_key", "proj2_data", tenant_id="tenant1", project_id="proj2"
        )
        p2_data = await memory_backend.get("shared_key", tenant_id="tenant1", project_id="proj2")
        assert p2_data is not None
        assert p2_data.data == "proj2_data"


class TestFileProjectMemory(TestProjectMemory):
    """Test FileProjectMemory implementation."""

    @pytest.fixture
    def memory_backend(self, acl_check, tmp_path) -> ProjectMemory:
        return FileProjectMemory(root_dir=tmp_path / "memory", acl_check=acl_check)

    @pytest.mark.asyncio
    async def test_put_and_get_basic(self, memory_backend):
        """Test basic put and get operations."""
        # Put an artifact
        artifact = await memory_backend.put(
            key="test_key", data="test data", meta={"type": "string"}, artifact_type="text"
        )

        assert artifact.key == "test_key"
        assert artifact.data == "test data"
        assert artifact.version == 1
        assert artifact.meta["type"] == "string"
        assert artifact.type == "text"

        # Get the artifact
        retrieved = await memory_backend.get("test_key")
        assert retrieved is not None
        assert retrieved.key == "test_key"
        assert retrieved.data == "test data"
        assert retrieved.version == 1

    @pytest.mark.asyncio
    async def test_versioning(self, memory_backend):
        """Test versioning functionality."""
        # Put multiple versions
        await memory_backend.put("versioned_key", "v1", meta={"version": "1"})
        await memory_backend.put("versioned_key", "v2", meta={"version": "2"})
        await memory_backend.put("versioned_key", "v3", meta={"version": "3"})

        # Get latest
        latest = await memory_backend.get("versioned_key")
        assert latest is not None
        assert latest.data == "v3"
        assert latest.version == 3

        # Get specific version
        v2 = await memory_backend.get("versioned_key", version=2)
        assert v2 is not None
        assert v2.data == "v2"
        assert v2.version == 2

        # List versions
        versions = await memory_backend.list_versions("versioned_key")
        assert versions == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_list_versions_empty(self, memory_backend):
        """Test listing versions for non-existent key."""
        versions = await memory_backend.list_versions("nonexistent")
        assert versions == []

    @pytest.mark.asyncio
    async def test_delete_specific_version(self, memory_backend):
        """Test deleting a specific version."""
        await memory_backend.put("delete_key", "v1")
        await memory_backend.put("delete_key", "v2")
        await memory_backend.put("delete_key", "v3")

        # Delete version 2
        result = await memory_backend.delete("delete_key", version=2)
        assert result is True

        # Version 2 should be gone
        v2 = await memory_backend.get("delete_key", version=2)
        assert v2 is None

        # Other versions should remain
        v1 = await memory_backend.get("delete_key", version=1)
        assert v1 is not None
        v3 = await memory_backend.get("delete_key", version=3)
        assert v3 is not None

        # List should not include deleted version
        versions = await memory_backend.list_versions("delete_key")
        assert versions == [1, 3]

    @pytest.mark.asyncio
    async def test_delete_all_versions(self, memory_backend):
        """Test deleting all versions of a key."""
        await memory_backend.put("delete_all_key", "v1")
        await memory_backend.put("delete_all_key", "v2")

        # Delete all
        result = await memory_backend.delete("delete_all_key")
        assert result is True

        # Key should be gone
        retrieved = await memory_backend.get("delete_all_key")
        assert retrieved is None

        versions = await memory_backend.list_versions("delete_all_key")
        assert versions == []

    @pytest.mark.asyncio
    async def test_acl_deny_write(self, memory_backend, acl_check):
        """Test ACL denial for write operations."""
        acl_check.return_value = False

        with pytest.raises(PermissionError, match="Access denied"):
            await memory_backend.put("denied_key", "data")

    @pytest.mark.asyncio
    async def test_acl_deny_read(self, memory_backend, acl_check):
        """Test ACL denial for read operations."""
        # First put with allow
        acl_check.return_value = True
        await memory_backend.put("read_denied_key", "data")

        # Then deny read
        acl_check.return_value = False

        with pytest.raises(PermissionError, match="Access denied"):
            await memory_backend.get("read_denied_key")

    @pytest.mark.asyncio
    async def test_bytes_data(self, memory_backend):
        """Test storing and retrieving bytes data."""
        binary_data = b"\x00\x01\x02\x03\xff"

        await memory_backend.put(key="binary_key", data=binary_data, artifact_type="binary")

        retrieved = await memory_backend.get("binary_key")
        assert retrieved is not None
        assert retrieved.data == binary_data
        assert isinstance(retrieved.data, bytes)

    @pytest.mark.asyncio
    async def test_tenant_project_isolation(self, memory_backend):
        """Test that tenants and projects are isolated."""
        # Put in different tenants/projects
        await memory_backend.put(
            "shared_key", "tenant1_data", tenant_id="tenant1", project_id="proj1"
        )
        await memory_backend.put(
            "shared_key", "tenant2_data", tenant_id="tenant2", project_id="proj1"
        )

        # Get from tenant1
        t1_data = await memory_backend.get("shared_key", tenant_id="tenant1", project_id="proj1")
        assert t1_data is not None
        assert t1_data.data == "tenant1_data"

        # Get from tenant2
        t2_data = await memory_backend.get("shared_key", tenant_id="tenant2", project_id="proj1")
        assert t2_data is not None
        assert t2_data.data == "tenant2_data"

        # Different projects
        await memory_backend.put(
            "shared_key", "proj2_data", tenant_id="tenant1", project_id="proj2"
        )
        p2_data = await memory_backend.get("shared_key", tenant_id="tenant1", project_id="proj2")
        assert p2_data is not None
        assert p2_data.data == "proj2_data"

    @pytest.mark.asyncio
    async def test_persistence_across_instances(self, acl_check, tmp_path):
        """Test that data persists across FileProjectMemory instances."""
        root_dir = tmp_path / "persistent_memory"

        # Create first instance and store data
        mem1 = FileProjectMemory(root_dir=root_dir, acl_check=acl_check)
        await mem1.put("persistent_key", "persistent_data", meta={"persistent": True})
        await mem1.put("persistent_key", "updated_data", meta={"updated": True})

        # Create second instance (simulating restart)
        mem2 = FileProjectMemory(root_dir=root_dir, acl_check=acl_check)

        # Data should still be there
        retrieved = await mem2.get("persistent_key")
        assert retrieved is not None
        assert retrieved.data == "updated_data"
        assert retrieved.version == 2
        assert retrieved.meta["updated"] is True

        # Check first version still has its meta
        v1 = await mem2.get("persistent_key", version=1)
        assert v1 is not None
        assert v1.data == "persistent_data"
        assert v1.meta["persistent"] is True

        versions = await mem2.list_versions("persistent_key")
        assert versions == [1, 2]


@pytest.mark.asyncio
async def test_performance_basic(tmp_path):
    """Basic performance test for both backends."""
    from unittest.mock import Mock

    acl_check = Mock(return_value=True)

    backends = [
        InMemProjectMemory(acl_check=acl_check),
        FileProjectMemory(root_dir=tmp_path / "perf_memory", acl_check=acl_check),
    ]

    for backend in backends:
        backend_name = type(backend).__name__

        # Performance test: 1000 puts
        start_time = time.time()
        for i in range(1000):
            await backend.put(f"perf_key_{i}", f"data_{i}", meta={"index": i})
        put_time = time.time() - start_time

        # Performance test: 1000 gets
        start_time = time.time()
        for i in range(1000):
            retrieved = await backend.get(f"perf_key_{i}")
            assert retrieved is not None
        get_time = time.time() - start_time

        print(f"{backend_name}: 1000 puts in {put_time:.2f}s, 1000 gets in {get_time:.2f}s")

        # Should be reasonably fast (less than 10 seconds total for both operations)
        assert put_time + get_time < 10.0


@pytest.mark.asyncio
async def test_concurrent_access(tmp_path):
    """Test concurrent access to memory backends."""
    from unittest.mock import Mock

    acl_check = Mock(return_value=True)

    backend = FileProjectMemory(root_dir=tmp_path / "concurrent_memory", acl_check=acl_check)

    async def concurrent_put(task_id: int):
        for i in range(10):
            await backend.put(f"concurrent_key_{task_id}", f"data_{task_id}_{i}")

    # Run 5 concurrent tasks
    tasks = [concurrent_put(i) for i in range(5)]
    await asyncio.gather(*tasks)

    # Verify all data is there
    total_versions = 0
    for task_id in range(5):
        versions = await backend.list_versions(f"concurrent_key_{task_id}")
        assert len(versions) == 10
        total_versions += len(versions)

    assert total_versions == 50

    # Verify no data corruption (all versions have correct data)
    for task_id in range(5):
        for version in range(1, 11):
            artifact = await backend.get(f"concurrent_key_{task_id}", version=version)
            assert artifact is not None
            expected_data = f"data_{task_id}_{version-1}"
            assert artifact.data == expected_data
