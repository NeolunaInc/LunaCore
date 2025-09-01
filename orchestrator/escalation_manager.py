import asyncio


class EscalationManager:
    """Manages escalation of failed tasks through a chain of agents/models
    with backoff and budget tracking."""

    def __init__(self, chain: list[str], backoff: list[float], budget: float = 100.0):
        """Initialize escalation manager.

        Args:
            chain: List of escalation levels
                (e.g., ["llama3:8b", "gpt-3.5-turbo", "gpt-4", "human"])
            backoff: List of backoff times in seconds for retries
            budget: Initial budget for costs (e.g., OpenAI API costs)
        """
        self.chain = chain
        self.backoff = backoff
        self.budget = budget
        self.current_cost = 0.0

    def escalate(self, current_level: int) -> str:
        """Get the next escalation level.

        Args:
            current_level: Current level index in the chain

        Returns:
            Next agent/model in the chain, or the last one if at end
        """
        if current_level + 1 < len(self.chain):
            return self.chain[current_level + 1]
        return self.chain[-1]  # Stay at last level (e.g., human)

    def get_backoff(self, attempt: int) -> float:
        """Get backoff time for the given attempt.

        Args:
            attempt: Attempt number (1-based)

        Returns:
            Backoff time in seconds
        """
        if attempt <= len(self.backoff):
            return self.backoff[attempt - 1]
        return self.backoff[-1]  # Use last backoff for further attempts

    def track_cost(self, cost: float) -> None:
        """Track the cost of an operation.

        Args:
            cost: Cost to add to total
        """
        self.current_cost += cost
        self.budget -= cost

    def can_afford(self, cost: float) -> bool:
        """Check if the budget can afford the given cost.

        Args:
            cost: Cost to check

        Returns:
            True if budget >= cost, False otherwise
        """
        return self.budget >= cost

    def is_at_end(self, level: int) -> bool:
        """Check if at the end of the escalation chain.

        Args:
            level: Current level index

        Returns:
            True if at the last level, False otherwise
        """
        return level >= len(self.chain) - 1

    async def wait_backoff(self, attempt: int) -> None:
        """Wait for the backoff time for the given attempt.

        Args:
            attempt: Attempt number (1-based)
        """
        backoff_time = self.get_backoff(attempt)
        await asyncio.sleep(backoff_time)
