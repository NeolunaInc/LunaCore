from typing import Any


class SimpleAllocator:
    """Simple resource allocator that resolves callables from steps."""

    def resolve(self, step: dict[str, Any]) -> Any:
        """Resolve the callable from a step dictionary.

        Args:
            step: Step dictionary containing 'callable' key

        Returns:
            The callable function

        Raises:
            ValueError: If callable is not found in step
        """
        if "callable" not in step:
            raise ValueError(f"No callable found in step: {step}")

        return step["callable"]
