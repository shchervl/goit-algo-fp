import random
from collections import Counter

import pytest

from task_07.monte_carlo import (
    SUM_RANGE,
    analytical_probabilities,
    comparison_table,
    empirical_probabilities,
    plot_comparison,
    roll_pair,
    simulate,
)


class TestRollPair:
    def test_returns_in_range(self):
        rng = random.Random(0)
        for _ in range(1000):
            s = roll_pair(rng)
            assert 2 <= s <= 12

    def test_deterministic_with_seed(self):
        a = [roll_pair(random.Random(42)) for _ in range(5)]
        b = [roll_pair(random.Random(42)) for _ in range(5)]
        assert a == b


class TestSimulate:
    def test_zero_rolls(self):
        assert simulate(0) == Counter()

    def test_count_sum_matches_rolls(self):
        n = 1000
        counts = simulate(n, seed=1)
        assert sum(counts.values()) == n

    def test_all_sums_in_valid_range(self):
        counts = simulate(10_000, seed=1)
        for s in counts:
            assert 2 <= s <= 12

    def test_reproducible_with_seed(self):
        assert simulate(500, seed=7) == simulate(500, seed=7)

    def test_negative_rolls_raises(self):
        with pytest.raises(ValueError, match="≥ 0"):
            simulate(-1)


class TestAnalytical:
    def test_all_sums_present(self):
        probs = analytical_probabilities()
        assert set(probs.keys()) == set(SUM_RANGE)

    def test_sum_to_one(self):
        probs = analytical_probabilities()
        assert sum(probs.values()) == pytest.approx(1.0)

    def test_specific_values(self):
        probs = analytical_probabilities()
        assert probs[2] == pytest.approx(1 / 36)
        assert probs[7] == pytest.approx(6 / 36)  # пік
        assert probs[12] == pytest.approx(1 / 36)

    def test_symmetric_around_seven(self):
        """P(s) = P(14 - s) для s ∈ [2, 12]."""
        probs = analytical_probabilities()
        for s in range(2, 8):
            assert probs[s] == pytest.approx(probs[14 - s])


class TestEmpirical:
    def test_empty_counts(self):
        probs = empirical_probabilities(Counter())
        assert probs == {s: 0.0 for s in SUM_RANGE}

    def test_sum_to_one_when_populated(self):
        counts = simulate(1000, seed=0)
        probs = empirical_probabilities(counts)
        assert sum(probs.values()) == pytest.approx(1.0)

    def test_missing_sum_is_zero(self):
        counts = Counter({7: 10})
        probs = empirical_probabilities(counts)
        assert probs[2] == 0.0
        assert probs[7] == 1.0

    def test_converges_to_analytical(self):
        """Закон великих чисел: 200к кидків → відхилення < 1% для кожної суми."""
        counts = simulate(200_000, seed=42)
        empirical = empirical_probabilities(counts)
        analytical = analytical_probabilities()
        for s in SUM_RANGE:
            assert abs(empirical[s] - analytical[s]) < 0.01, f"s={s}"


class TestComparisonTable:
    def test_includes_all_sums(self):
        emp = {s: 0.1 for s in SUM_RANGE}
        ana = analytical_probabilities()
        table = comparison_table(emp, ana)
        for s in SUM_RANGE:
            assert str(s) in table

    def test_includes_percentages(self):
        table = comparison_table(
            empirical_probabilities(simulate(1000, seed=0)),
            analytical_probabilities(),
        )
        assert "%" in table


class TestPlotSmoke:
    def test_save_png(self, tmp_path):
        import matplotlib

        matplotlib.use("Agg")
        out = tmp_path / "comparison.png"
        plot_comparison(
            empirical_probabilities(simulate(1000, seed=0)),
            analytical_probabilities(),
            save=str(out),
        )
        assert out.exists() and out.stat().st_size > 0
