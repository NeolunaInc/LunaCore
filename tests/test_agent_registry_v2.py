from unittest.mock import AsyncMock

import pytest

from services.agent_registry.api import AgentRegistry, AgentRegistryAPI
from services.sandbox.runner import AgentSandboxRunner, SandboxResult, TestCase


class TestAgentRegistry:
    """Test cases for AgentRegistry class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.registry = AgentRegistry()

    def test_register_agent_success(self):
        """Test successful agent registration."""
        agent_code = """
class TestAgent:
    def run(self, input_data):
        return {"result": "success", "input": input_data}
"""

        agent = self.registry.register_agent(
            name="test_agent", version="v1.0.0", code=agent_code, metadata={"author": "test"}
        )

        assert agent.name == "test_agent"
        assert agent.version == "v1.0.0"
        assert agent.status == "testing"
        assert agent.metadata["author"] == "test"

    def test_register_agent_invalid_version(self):
        """Test registration with invalid version format."""
        with pytest.raises(ValueError, match="Invalid version format"):
            self.registry.register_agent(
                name="test_agent",
                version="1.0.0",  # Missing 'v' prefix
                code="class TestAgent: pass",
            )

    def test_register_duplicate_version(self):
        """Test registration of duplicate version."""
        agent_code = "class TestAgent: pass"

        # Register first time
        self.registry.register_agent("test_agent", "v1.0.0", agent_code)

        # Try to register same version again
        with pytest.raises(ValueError, match="Version v1.0.0 already exists"):
            self.registry.register_agent("test_agent", "v1.0.0", agent_code)

    def test_get_agent_latest(self):
        """Test getting latest agent version."""
        agent_code = "class TestAgent: pass"

        # Register multiple versions
        self.registry.register_agent("test_agent", "v1.0.0", agent_code)
        self.registry.register_agent("test_agent", "v1.1.0", agent_code)
        self.registry.register_agent("test_agent", "v1.0.1", agent_code)

        # Get latest (should be v1.1.0 due to semantic versioning sort)
        agent = self.registry.get_agent("test_agent")
        assert agent is not None
        assert agent.version == "v1.1.0"

    def test_get_agent_specific_version(self):
        """Test getting specific agent version."""
        agent_code = "class TestAgent: pass"

        self.registry.register_agent("test_agent", "v1.0.0", agent_code)
        self.registry.register_agent("test_agent", "v1.1.0", agent_code)

        agent = self.registry.get_agent("test_agent", "v1.0.0")
        assert agent is not None
        assert agent.version == "v1.0.0"

    def test_get_agent_not_found(self):
        """Test getting non-existent agent."""
        agent = self.registry.get_agent("non_existent")
        assert agent is None

    def test_update_agent_status(self):
        """Test updating agent status."""
        agent_code = "class TestAgent: pass"

        self.registry.register_agent("test_agent", "v1.0.0", agent_code)

        # Update status
        success = self.registry.update_agent_status("test_agent", "v1.0.0", "active")
        assert success

        # Verify status changed
        agent = self.registry.get_agent("test_agent", "v1.0.0")
        assert agent is not None
        assert agent.status == "active"

    def test_update_agent_status_invalid(self):
        """Test updating status with invalid value."""
        agent_code = "class TestAgent: pass"

        self.registry.register_agent("test_agent", "v1.0.0", agent_code)

        with pytest.raises(ValueError, match="Invalid status"):
            self.registry.update_agent_status("test_agent", "v1.0.0", "invalid_status")

    def test_list_agents(self):
        """Test listing all agents."""
        # Register multiple agents
        self.registry.register_agent("agent1", "v1.0.0", "class Agent1: pass")
        self.registry.register_agent("agent1", "v1.1.0", "class Agent1: pass")
        self.registry.register_agent("agent2", "v1.0.0", "class Agent2: pass")

        # Set one as active
        self.registry.update_agent_status("agent1", "v1.1.0", "active")

        agents = self.registry.list_agents()

        assert len(agents) == 2

        # Check agent1
        agent1 = next(a for a in agents if a["name"] == "agent1")
        assert agent1["latest_version"] == "v1.1.0"
        assert agent1["active_version"] == "v1.1.0"
        assert len(agent1["versions"]) == 2

        # Check agent2
        agent2 = next(a for a in agents if a["name"] == "agent2")
        assert agent2["latest_version"] == "v1.0.0"
        assert agent2["active_version"] is None

    def test_delete_agent_version(self):
        """Test deleting agent version."""
        agent_code = "class TestAgent: pass"

        self.registry.register_agent("test_agent", "v1.0.0", agent_code)
        self.registry.register_agent("test_agent", "v1.1.0", agent_code)

        # Delete version
        success = self.registry.delete_agent_version("test_agent", "v1.0.0")
        assert success

        # Verify deletion
        agent = self.registry.get_agent("test_agent", "v1.0.0")
        assert agent is None

        # Verify other version still exists
        agent = self.registry.get_agent("test_agent", "v1.1.0")
        assert agent is not None

    def test_get_agent_history(self):
        """Test getting agent version history."""
        agent_code = "class TestAgent: pass"

        self.registry.register_agent("test_agent", "v1.0.0", agent_code)
        self.registry.register_agent("test_agent", "v1.1.0", agent_code)

        history = self.registry.get_agent_history("test_agent")

        assert len(history) == 2
        # Should be sorted with latest first
        assert history[0]["version"] == "v1.1.0"
        assert history[1]["version"] == "v1.0.0"


class TestAgentRegistryAPI:
    """Test cases for AgentRegistryAPI class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.registry = AgentRegistry()
        self.memory = AsyncMock()
        self.api = AgentRegistryAPI(self.registry, self.memory)

    @pytest.mark.asyncio
    async def test_register_agent_endpoint_success(self):
        """Test successful agent registration via API."""
        agent_code = "class TestAgent: pass"

        result = await self.api.register_agent_endpoint(
            name="test_agent", version="v1.0.0", code=agent_code, metadata={"author": "test"}
        )

        assert result["success"] is True
        assert result["agent"]["name"] == "test_agent"
        assert result["agent"]["version"] == "v1.0.0"

        # Verify memory storage was called
        self.memory.put.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_agent_endpoint_failure(self):
        """Test failed agent registration via API."""
        result = await self.api.register_agent_endpoint(
            name="test_agent", version="invalid_version", code="class TestAgent: pass"
        )

        assert result["success"] is False
        assert "Invalid version format" in result["error"]

    @pytest.mark.asyncio
    async def test_get_agent_endpoint_success(self):
        """Test successful agent retrieval via API."""
        agent_code = "class TestAgent: pass"

        # Register agent first
        await self.api.register_agent_endpoint("test_agent", "v1.0.0", agent_code)

        result = await self.api.get_agent_endpoint("test_agent", "v1.0.0")

        assert result["success"] is True
        assert result["agent"]["name"] == "test_agent"

    @pytest.mark.asyncio
    async def test_get_agent_endpoint_not_found(self):
        """Test agent retrieval for non-existent agent via API."""
        result = await self.api.get_agent_endpoint("non_existent", "v1.0.0")

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_update_status_endpoint_success(self):
        """Test successful status update via API."""
        agent_code = "class TestAgent: pass"

        # Register agent first
        await self.api.register_agent_endpoint("test_agent", "v1.0.0", agent_code)

        result = await self.api.update_status_endpoint("test_agent", "v1.0.0", "active")

        assert result["success"] is True
        assert "status updated" in result["message"]

        # Verify memory update was called
        assert self.memory.put.call_count == 2  # Register + update

    @pytest.mark.asyncio
    async def test_list_agents_endpoint(self):
        """Test listing agents via API."""
        # Register agents
        await self.api.register_agent_endpoint("agent1", "v1.0.0", "class Agent1: pass")
        await self.api.register_agent_endpoint("agent2", "v1.0.0", "class Agent2: pass")

        result = await self.api.list_agents_endpoint()

        assert result["success"] is True
        assert result["count"] == 2
        assert len(result["agents"]) == 2

    @pytest.mark.asyncio
    async def test_delete_agent_endpoint_success(self):
        """Test successful agent deletion via API."""
        agent_code = "class TestAgent: pass"

        # Register agent first
        await self.api.register_agent_endpoint("test_agent", "v1.0.0", agent_code)

        result = await self.api.delete_agent_endpoint("test_agent", "v1.0.0")

        assert result["success"] is True
        assert "deleted successfully" in result["message"]


class TestAgentSandboxRunner:
    """Test cases for AgentSandboxRunner class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.registry = AgentRegistry()
        self.runner = AgentSandboxRunner(self.registry)

    def test_calculate_score_perfect_match(self):
        """Test score calculation for perfect match."""
        actual = {"result": "success", "value": 42}
        expected = {"result": "success", "value": 42}

        score = self.runner._calculate_score(actual, expected)
        assert score == 1.0

    def test_calculate_score_partial_match(self):
        """Test score calculation for partial match."""
        actual = {"result": "success", "value": 42}
        expected = {"result": "success", "value": 43}

        score = self.runner._calculate_score(actual, expected)
        assert score == 1.0  # Same keys, different values

    def test_calculate_score_no_match(self):
        """Test score calculation for no match."""
        actual = {"result": "success"}
        expected = {"status": "ok"}

        score = self.runner._calculate_score(actual, expected)
        assert score == 0.0

    @pytest.mark.asyncio
    async def test_run_agent_test_success(self):
        """Test successful agent test execution."""
        # Register a simple agent
        agent_code = """
class TestAgent:
    def run(self, input_data):
        return {"result": "success", "input": input_data}
"""
        self.registry.register_agent("test_agent", "v1.0.0", agent_code)

        test_case = TestCase(
            name="test_success",
            input_data={"test": "data"},
            expected_output={"result": "success", "input": {"test": "data"}},
        )

        result = await self.runner.run_agent_test("test_agent", "v1.0.0", test_case)

        assert isinstance(result, SandboxResult)
        assert result.agent_name == "test_agent"
        assert result.agent_version == "v1.0.0"
        assert result.success is True
        assert result.score == 1.0

    @pytest.mark.asyncio
    async def test_run_agent_test_timeout(self):
        """Test agent test execution with timeout."""
        # Register an agent that sleeps too long
        agent_code = """
import time
class TestAgent:
    def run(self, input_data):
        time.sleep(10)  # Sleep longer than timeout
        return {"result": "success"}
"""
        self.registry.register_agent("test_agent", "v1.0.0", agent_code)

        test_case = TestCase(
            name="test_timeout",
            input_data={},
            expected_output={"result": "success"},
            timeout=1.0,  # Short timeout
        )

        result = await self.runner.run_agent_test("test_agent", "v1.0.0", test_case)

        assert result.success is False
        assert "timeout" in result.errors.lower()

    @pytest.mark.asyncio
    async def test_run_agent_validation_suite(self):
        """Test running complete validation suite."""
        # Register agent
        agent_code = """
class TestAgent:
    def run(self, input_data):
        return {"result": "success", "input": input_data}
"""
        self.registry.register_agent("test_agent", "v1.0.0", agent_code)

        test_cases = [
            TestCase(
                name="test1",
                input_data={"test": "data1"},
                expected_output={"result": "success", "input": {"test": "data1"}},
                weight=1.0,
            ),
            TestCase(
                name="test2",
                input_data={"test": "data2"},
                expected_output={"result": "success", "input": {"test": "data2"}},
                weight=2.0,
            ),
        ]

        result = await self.runner.run_agent_validation_suite("test_agent", "v1.0.0", test_cases)

        assert result["agent_name"] == "test_agent"
        assert result["agent_version"] == "v1.0.0"
        assert result["overall_score"] == 1.0
        assert result["successful_tests"] == 2
        assert result["total_tests"] == 2
        assert len(result["results"]) == 2

    @pytest.mark.asyncio
    async def test_validate_agent_for_promotion_success(self):
        """Test agent promotion validation with success."""
        # Register agent
        agent_code = """
class TestAgent:
    def run(self, input_data):
        return {"result": "success", "input": input_data}
"""
        self.registry.register_agent("test_agent", "v1.0.0", agent_code)

        test_cases = [
            TestCase(
                name="test1",
                input_data={"test": "data"},
                expected_output={"result": "success", "input": {"test": "data"}},
            )
        ]

        result = await self.runner.validate_agent_for_promotion(
            "test_agent", "v1.0.0", test_cases, min_score=0.8
        )

        assert result["can_promote"] is True
        assert result["overall_score"] >= 0.8

        # Verify agent status was updated
        agent = self.registry.get_agent("test_agent", "v1.0.0")
        assert agent is not None
        assert agent.status == "active"

    @pytest.mark.asyncio
    async def test_validate_agent_for_promotion_failure(self):
        """Test agent promotion validation with failure."""
        # Register agent that returns wrong output
        agent_code = """
class TestAgent:
    def run(self, input_data):
        return {"result": "failure"}
"""
        self.registry.register_agent("test_agent", "v1.0.0", agent_code)

        test_cases = [
            TestCase(
                name="test1", input_data={"test": "data"}, expected_output={"result": "success"}
            )
        ]

        result = await self.runner.validate_agent_for_promotion(
            "test_agent", "v1.0.0", test_cases, min_score=0.8
        )

        assert result["can_promote"] is False
        assert result["overall_score"] < 0.8

        # Verify agent status was NOT updated
        agent = self.registry.get_agent("test_agent", "v1.0.0")
        assert agent is not None
        assert agent.status == "testing"
