import random
from typing import Any


class SolutionResolver:
    def __init__(self):
        pass

    def generate_variants(
        self, base_solution: dict[str, Any], num_variants: int = 3
    ) -> list[dict[str, Any]]:
        """
        Generate variants of the base solution.
        For simplicity, modify a parameter randomly.
        """
        variants = []
        for _ in range(num_variants):
            variant = base_solution.copy()
            # Assume base_solution has a 'param' key
            if "param" in variant:
                variant["param"] = random.randint(1, 10)
            variants.append(variant)
        return variants

    def score_solutions(self, solutions: list[dict[str, Any]]) -> list[float]:
        """
        Score the solutions. For demo, random scores.
        In real scenario, based on performance metrics.
        """
        return [random.uniform(0, 1) for _ in solutions]

    def select_best(self, solutions: list[dict[str, Any]], scores: list[float]) -> dict[str, Any]:
        """
        Select the solution with the highest score.
        """
        if not solutions or not scores:
            raise ValueError("No solutions or scores provided")
        best_index = scores.index(max(scores))
        return solutions[best_index]
