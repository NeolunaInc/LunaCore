from typing import Any


class CreativeEnhancementAgent:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    def generate_suggestions(self, task: dict[str, Any]) -> list[str]:
        """
        Generate creative suggestions for a given task.
        For now, returns static suggestions.
        """
        if not self.enabled:
            return []

        base_suggestions = [
            "Consider using a more efficient algorithm for this task.",
            "Add error handling to make the code more robust.",
            "Optimize for performance by reducing unnecessary computations.",
            "Improve readability with better variable names and comments.",
            "Explore alternative libraries or frameworks for this functionality.",
        ]

        # Customize based on task type if available
        task_type = task.get("type", "custom")
        if task_type == "generate_code":
            base_suggestions.append("Use type hints for better code quality.")
        elif task_type == "test":
            base_suggestions.append("Increase test coverage with edge cases.")

        return base_suggestions

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False
