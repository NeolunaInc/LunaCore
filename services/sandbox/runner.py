import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from services.agent_registry.api import AgentRegistry


@dataclass
class SandboxResult:
    """Result of running an agent in the sandbox."""

    agent_name: str
    agent_version: str
    success: bool
    execution_time: float
    output: str
    errors: str
    score: float
    metadata: dict[str, Any]
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class TestCase:
    """Test case for agent validation."""

    name: str
    input_data: dict[str, Any]
    expected_output: dict[str, Any]
    timeout: float = 30.0
    weight: float = 1.0


class AgentSandboxRunner:
    """Sandbox environment for testing and validating agents."""

    def __init__(self, registry: AgentRegistry, sandbox_dir: str = "/tmp/agent_sandbox"):
        self.registry = registry
        self.sandbox_dir = Path(sandbox_dir)
        self.logger = logging.getLogger(__name__)

        # Create sandbox directory
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)

    def _create_sandbox_environment(self, agent_name: str, agent_version: str) -> Path:
        """Create isolated sandbox environment for agent execution."""
        sandbox_path = self.sandbox_dir / f"{agent_name}_{agent_version}_{int(time.time())}"
        sandbox_path.mkdir(parents=True, exist_ok=True)

        # Create basic Python environment files
        requirements_path = sandbox_path / "requirements.txt"
        requirements_path.write_text("")

        return sandbox_path

    def _write_agent_code(self, sandbox_path: Path, agent_code: str) -> Path:
        """Write agent code to sandbox environment."""
        agent_file = sandbox_path / "agent.py"
        agent_file.write_text(agent_code)
        return agent_file

    def _create_test_runner(self, sandbox_path: Path, test_case: TestCase) -> Path:
        """Create test runner script for the agent."""
        runner_code = f"""
import json
import sys
import time
from agent import *

def run_test():
    try:
        # Load test input
        input_data = {json.dumps(test_case.input_data)}

        # Create agent instance (assuming Agent class exists)
        if 'Agent' in globals():
            agent = Agent()
        else:
            # Try to find the main agent class
            agent_classes = [
                cls for cls in globals().values()
                if isinstance(cls, type) and hasattr(cls, 'run')
            ]
            if agent_classes:
                agent = agent_classes[0]()
            else:
                raise RuntimeError("No Agent class found in agent code")

        start_time = time.time()

        # Run agent with test input
        if hasattr(agent, 'run'):
            result = agent.run(input_data)
        elif hasattr(agent, '__call__'):
            result = agent(input_data)
        else:
            raise RuntimeError("Agent has no run method or is not callable")

        execution_time = time.time() - start_time

        # Validate result structure
        if not isinstance(result, dict):
            result = {{"output": result}}

        # Add execution metadata
        result["_execution_time"] = execution_time
        result["_success"] = True

        print(json.dumps(result))

    except Exception as e:
        error_result = {{
            "_success": False,
            "_error": str(e),
            "_execution_time": time.time() - time.time()  # Will be 0
        }}
        print(json.dumps(error_result))

if __name__ == "__main__":
    run_test()
"""

        runner_file = sandbox_path / "test_runner.py"
        runner_file.write_text(runner_code)
        return runner_file

    async def run_agent_test(
        self, agent_name: str, agent_version: str, test_case: TestCase
    ) -> SandboxResult:
        """Run a single test case against an agent."""
        start_time = time.time()

        try:
            # Get agent from registry
            agent_version_obj = self.registry.get_agent(agent_name, agent_version)
            if not agent_version_obj:
                raise ValueError(f"Agent {agent_name} version {agent_version} not found")

            # Create sandbox environment
            sandbox_path = self._create_sandbox_environment(agent_name, agent_version)

            # Write agent code
            self._write_agent_code(sandbox_path, agent_version_obj.code)

            # Create test runner
            runner_file = self._create_test_runner(sandbox_path, test_case)

            # Execute test in subprocess
            process = await asyncio.create_subprocess_exec(
                "python3",
                str(runner_file),
                cwd=str(sandbox_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=test_case.timeout
                )

                execution_time = time.time() - start_time

                # Parse output
                output_str = stdout.decode("utf-8").strip()
                error_str = stderr.decode("utf-8").strip()

                try:
                    result_data = json.loads(output_str)
                    success = result_data.get("_success", False)
                    execution_time = result_data.get("_execution_time", execution_time)

                    # Calculate score based on output matching expected
                    score = self._calculate_score(result_data, test_case.expected_output)

                except json.JSONDecodeError:
                    success = False
                    score = 0.0
                    result_data = {"raw_output": output_str}

                # Clean up sandbox
                await self._cleanup_sandbox(sandbox_path)

                return SandboxResult(
                    agent_name=agent_name,
                    agent_version=agent_version,
                    success=success,
                    execution_time=execution_time,
                    output=output_str,
                    errors=error_str,
                    score=score,
                    metadata={
                        "test_case": test_case.name,
                        "sandbox_path": str(sandbox_path),
                        "result_data": result_data,
                    },
                    timestamp=datetime.utcnow(),
                )

            except TimeoutError:
                process.kill()
                await process.wait()

                execution_time = time.time() - start_time
                await self._cleanup_sandbox(sandbox_path)

                return SandboxResult(
                    agent_name=agent_name,
                    agent_version=agent_version,
                    success=False,
                    execution_time=execution_time,
                    output="",
                    errors=f"Test timeout after {test_case.timeout}s",
                    score=0.0,
                    metadata={"test_case": test_case.name, "timeout": True},
                    timestamp=datetime.utcnow(),
                )

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Failed to run agent test: {str(e)}")

            return SandboxResult(
                agent_name=agent_name,
                agent_version=agent_version,
                success=False,
                execution_time=execution_time,
                output="",
                errors=str(e),
                score=0.0,
                metadata={"test_case": test_case.name, "error": str(e)},
                timestamp=datetime.utcnow(),
            )

    def _calculate_score(
        self, actual_output: dict[str, Any], expected_output: dict[str, Any]
    ) -> float:
        """Calculate test score based on output comparison."""
        if not isinstance(actual_output, dict) or not isinstance(expected_output, dict):
            return 0.0

        # Remove metadata fields from comparison
        actual_clean = {k: v for k, v in actual_output.items() if not k.startswith("_")}
        expected_clean = {k: v for k, v in expected_output.items() if not k.startswith("_")}

        if actual_clean == expected_clean:
            return 1.0

        # Partial scoring based on matching keys
        matching_keys = set(actual_clean.keys()) & set(expected_clean.keys())
        if not matching_keys:
            return 0.0

        total_keys = len(set(actual_clean.keys()) | set(expected_clean.keys()))
        return len(matching_keys) / total_keys

    async def _cleanup_sandbox(self, sandbox_path: Path):
        """Clean up sandbox environment."""
        try:
            import shutil

            shutil.rmtree(sandbox_path)
        except Exception as e:
            self.logger.warning(f"Failed to cleanup sandbox {sandbox_path}: {str(e)}")

    async def run_agent_validation_suite(
        self, agent_name: str, agent_version: str, test_cases: list[TestCase]
    ) -> dict[str, Any]:
        """Run complete validation suite for an agent."""
        results = []

        for test_case in test_cases:
            result = await self.run_agent_test(agent_name, agent_version, test_case)
            results.append(result)

        # Calculate overall score
        total_weight = sum(tc.weight for tc in test_cases)
        weighted_score = sum(r.score * tc.weight for r, tc in zip(results, test_cases, strict=True))
        overall_score = weighted_score / total_weight if total_weight > 0 else 0.0

        # Count successes
        successful_tests = sum(1 for r in results if r.success)
        total_tests = len(test_cases)

        return {
            "agent_name": agent_name,
            "agent_version": agent_version,
            "overall_score": overall_score,
            "successful_tests": successful_tests,
            "total_tests": total_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0.0,
            "results": [r.to_dict() for r in results],
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def validate_agent_for_promotion(
        self,
        agent_name: str,
        agent_version: str,
        test_cases: list[TestCase],
        min_score: float = 0.8,
    ) -> dict[str, Any]:
        """Validate agent and determine if it can be promoted to active status."""
        validation_result = await self.run_agent_validation_suite(
            agent_name, agent_version, test_cases
        )

        can_promote = validation_result["overall_score"] >= min_score

        validation_result["can_promote"] = can_promote
        validation_result["min_score_required"] = min_score

        if can_promote:
            # Update agent status to active
            success = self.registry.update_agent_status(agent_name, agent_version, "active")
            validation_result["status_update_success"] = success
        else:
            validation_result["status_update_success"] = False

        return validation_result
