"""Жадібний vs динамічне програмування для вибору їжі з максимальними калоріями.

Це класична задача 0/1 ранця: набір страв з вартістю/калорійністю, обмежений бюджет.
Жадібний алгоритм бере локально найвигідніше (калорії/вартість) — швидко але неоптимально.
DP знаходить істинно оптимальний набір через побудову таблиці підзадач — O(n·B).
"""

from __future__ import annotations

from typing import NamedTuple

Items = dict[str, dict[str, int]]


class Selection(NamedTuple):
    """Результат вибору: список страв + сумарні вартість і калорії."""

    items: list[str]
    total_cost: int
    total_calories: int


def greedy_algorithm(items: Items, budget: int) -> Selection:
    """Жадібний: сортуємо за калорії/вартість, беремо доки бюджет дозволяє.

    Складність: O(n log n) на сортування + O(n) на вибір = O(n log n).
    Гарантує локальний оптимум, але не глобальний — для 0/1 ранця може давати гірший результат.
    """
    if budget < 0:
        raise ValueError(f"budget має бути ≥ 0, отримано {budget}")

    sorted_items = sorted(
        items.items(),
        key=lambda kv: kv[1]["calories"] / kv[1]["cost"],
        reverse=True,
    )
    selected: list[str] = []
    cost = 0
    calories = 0
    for name, info in sorted_items:
        if cost + info["cost"] <= budget:
            selected.append(name)
            cost += info["cost"]
            calories += info["calories"]
    return Selection(selected, cost, calories)


def dynamic_programming(items: Items, budget: int) -> Selection:
    """0/1 ранець через DP: завжди оптимальний набір.

    dp[i][b] = максимум калорій, використовуючи перші i страв і бюджет b.
    Рекурентність: dp[i][b] = max(не брати i-у, брати якщо влізає).
    Складність: O(n·B) за часом та пам'яттю. Backtracking відновлює набір.
    """
    if budget < 0:
        raise ValueError(f"budget має бути ≥ 0, отримано {budget}")

    names = list(items.keys())
    n = len(names)
    if n == 0 or budget == 0:
        return Selection([], 0, 0)

    # dp[i][b] = max calories using items[0..i-1] within budget b
    dp = [[0] * (budget + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        cost_i = items[names[i - 1]]["cost"]
        cal_i = items[names[i - 1]]["calories"]
        for b in range(budget + 1):
            dp[i][b] = dp[i - 1][b]  # варіант: не брати i-у страву
            if cost_i <= b:
                with_item = dp[i - 1][b - cost_i] + cal_i
                if with_item > dp[i][b]:
                    dp[i][b] = with_item

    # Backtracking — відновлюємо вибраний набір
    selected: list[str] = []
    b = budget
    for i in range(n, 0, -1):
        if dp[i][b] != dp[i - 1][b]:  # i-у страву взяли
            name = names[i - 1]
            selected.append(name)
            b -= items[name]["cost"]
    selected.reverse()

    total_cost = sum(items[name]["cost"] for name in selected)
    return Selection(selected, total_cost, dp[n][budget])
