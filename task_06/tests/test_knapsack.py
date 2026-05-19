import pytest

from task_06.knapsack import Selection, dynamic_programming, greedy_algorithm

ITEMS = {
    "pizza":     {"cost": 50, "calories": 300},
    "hamburger": {"cost": 40, "calories": 250},
    "hot-dog":   {"cost": 30, "calories": 200},
    "pepsi":     {"cost": 10, "calories": 100},
    "cola":      {"cost": 15, "calories": 220},
    "potato":    {"cost": 25, "calories": 350},
}


class TestGreedy:
    def test_empty_items(self):
        assert greedy_algorithm({}, budget=100) == Selection([], 0, 0)

    def test_zero_budget(self):
        assert greedy_algorithm(ITEMS, budget=0) == Selection([], 0, 0)

    def test_single_item_fits(self):
        result = greedy_algorithm({"a": {"cost": 10, "calories": 50}}, budget=20)
        assert result.items == ["a"]
        assert result.total_cost == 10
        assert result.total_calories == 50

    def test_single_item_too_expensive(self):
        result = greedy_algorithm({"a": {"cost": 100, "calories": 50}}, budget=20)
        assert result == Selection([], 0, 0)

    def test_picks_best_ratio_first(self):
        """cola має найкраще кал/$ (220/15 ≈ 14.67) — має бути обрана першою."""
        result = greedy_algorithm(ITEMS, budget=15)
        assert result.items == ["cola"]

    def test_canonical_budget_100(self):
        """Документує суб-оптимальну поведінку жадібного при budget=100."""
        result = greedy_algorithm(ITEMS, budget=100)
        # cola(15) + potato(25) + pepsi(10) + hot-dog(30) = 80
        # калорій: 220 + 350 + 100 + 200 = 870
        assert sorted(result.items) == sorted(["cola", "potato", "pepsi", "hot-dog"])
        assert result.total_cost == 80
        assert result.total_calories == 870

    def test_negative_budget_raises(self):
        with pytest.raises(ValueError, match="≥ 0"):
            greedy_algorithm(ITEMS, budget=-1)

    def test_never_exceeds_budget(self):
        for budget in range(0, 200, 7):
            assert greedy_algorithm(ITEMS, budget).total_cost <= budget


class TestDynamicProgramming:
    def test_empty_items(self):
        assert dynamic_programming({}, budget=100) == Selection([], 0, 0)

    def test_zero_budget(self):
        assert dynamic_programming(ITEMS, budget=0) == Selection([], 0, 0)

    def test_single_item_fits(self):
        result = dynamic_programming({"a": {"cost": 10, "calories": 50}}, budget=20)
        assert result.items == ["a"]
        assert result.total_calories == 50

    def test_single_item_too_expensive(self):
        result = dynamic_programming({"a": {"cost": 100, "calories": 50}}, budget=20)
        assert result == Selection([], 0, 0)

    def test_canonical_budget_100_beats_greedy(self):
        """DP знаходить кращий набір ніж greedy: pizza+cola+potato+pepsi = 970 кал."""
        result = dynamic_programming(ITEMS, budget=100)
        assert sorted(result.items) == sorted(["pizza", "cola", "potato", "pepsi"])
        assert result.total_cost == 100
        assert result.total_calories == 970  # vs 870 у greedy

    def test_negative_budget_raises(self):
        with pytest.raises(ValueError, match="≥ 0"):
            dynamic_programming(ITEMS, budget=-1)

    def test_never_exceeds_budget(self):
        for budget in range(0, 200, 7):
            assert dynamic_programming(ITEMS, budget).total_cost <= budget

    def test_dp_ge_greedy(self):
        """DP завжди ≥ greedy за калорійністю (бо знаходить оптимум)."""
        for budget in range(0, 200, 5):
            dp = dynamic_programming(ITEMS, budget)
            gr = greedy_algorithm(ITEMS, budget)
            assert dp.total_calories >= gr.total_calories, f"budget={budget}"

    def test_all_items_fit_when_budget_sufficient(self):
        """Якщо бюджет покриває всі страви, беремо всі."""
        total_cost = sum(info["cost"] for info in ITEMS.values())
        total_cal = sum(info["calories"] for info in ITEMS.values())
        result = dynamic_programming(ITEMS, budget=total_cost)
        assert sorted(result.items) == sorted(ITEMS.keys())
        assert result.total_cost == total_cost
        assert result.total_calories == total_cal


class TestSelectionType:
    def test_tuple_unpacking(self):
        items, cost, calories = greedy_algorithm(ITEMS, 50)
        assert isinstance(items, list)
        assert isinstance(cost, int)
        assert isinstance(calories, int)

    def test_attribute_access(self):
        result = greedy_algorithm(ITEMS, 50)
        assert result.items is not None
        assert result.total_cost >= 0
        assert result.total_calories >= 0
