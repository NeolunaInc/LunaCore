import time
from collections.abc import Callable
from typing import Any


class CostTracker:
    def __init__(self, budget_limit: float = 100.0, alert_threshold: float = 0.8):
        self.budget_limit = budget_limit
        self.alert_threshold = alert_threshold
        self.current_cost = 0.0
        self.costs: list[dict[str, Any]] = []
        self.alert_callback: Callable[[float], None] | None = None

    def add_cost(
        self, amount: float, description: str, metadata: dict[str, Any] | None = None
    ) -> None:
        """
        Add a cost entry.
        """
        self.current_cost += amount
        entry = {
            "timestamp": time.time(),
            "amount": amount,
            "description": description,
            "metadata": metadata or {},
        }
        self.costs.append(entry)
        self._check_budget_alert()

    def _check_budget_alert(self) -> None:
        """
        Check if budget alert should be triggered.
        """
        if self.current_cost >= self.budget_limit * self.alert_threshold and self.alert_callback:
            self.alert_callback(self.current_cost)

    def get_total_cost(self) -> float:
        """
        Get the total cost incurred.
        """
        return self.current_cost

    def get_costs_by_type(self, cost_type: str) -> list[dict[str, Any]]:
        """
        Get costs filtered by type (from metadata).
        """
        return [c for c in self.costs if c["metadata"].get("type") == cost_type]

    def set_alert_callback(self, callback: Callable[[float], None]) -> None:
        """
        Set the callback for budget alerts.
        """
        self.alert_callback = callback

    def reset(self) -> None:
        """
        Reset the tracker.
        """
        self.current_cost = 0.0
        self.costs = []


# Example usage for OpenAI API
def track_openai_cost(tracker: CostTracker, tokens_used: int, model: str = "gpt-3.5-turbo") -> None:
    """
    Track cost for OpenAI API usage.
    Approximate cost per 1K tokens: $0.002 for gpt-3.5-turbo
    """
    cost_per_1k = 0.002  # Example rate
    amount = (tokens_used / 1000) * cost_per_1k
    tracker.add_cost(
        amount, f"OpenAI {model} usage", {"type": "api", "tokens": tokens_used, "model": model}
    )
