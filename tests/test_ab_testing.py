import pytest

from orchestrator.solution_resolver.resolver import SolutionResolver


class TestSolutionResolver:
    def test_generate_variants(self):
        resolver = SolutionResolver()
        base = {"param": 5, "other": "value"}
        variants = resolver.generate_variants(base, 2)
        assert len(variants) == 2
        for variant in variants:
            assert "param" in variant
            assert isinstance(variant["param"], int)
            assert 1 <= variant["param"] <= 10
            assert variant["other"] == "value"

    def test_score_solutions(self):
        resolver = SolutionResolver()
        solutions = [{"id": 1}, {"id": 2}]
        scores = resolver.score_solutions(solutions)
        assert len(scores) == 2
        for score in scores:
            assert 0 <= score <= 1

    def test_select_best(self):
        resolver = SolutionResolver()
        solutions = [{"id": 1}, {"id": 2}, {"id": 3}]
        scores = [0.5, 0.9, 0.3]
        best = resolver.select_best(solutions, scores)
        assert best["id"] == 2  # Highest score

    def test_select_best_empty(self):
        resolver = SolutionResolver()
        with pytest.raises(ValueError):
            resolver.select_best([], [])
