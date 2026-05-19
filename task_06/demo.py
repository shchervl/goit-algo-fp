"""Демо: порівнюємо жадібний vs DP на класичному наборі їжі.

Запуск:
    uv run python -m task_06.demo
"""

from __future__ import annotations

from task_06.knapsack import Selection, dynamic_programming, greedy_algorithm

ITEMS = {
    "pizza":     {"cost": 50, "calories": 300},
    "hamburger": {"cost": 40, "calories": 250},
    "hot-dog":   {"cost": 30, "calories": 200},
    "pepsi":     {"cost": 10, "calories": 100},
    "cola":      {"cost": 15, "calories": 220},
    "potato":    {"cost": 25, "calories": 350},
}


def _print_result(name: str, result: Selection, budget: int) -> None:
    print(f"  {name}:")
    print(f"    обрано:      {', '.join(result.items) or '—'}")
    print(f"    вартість:    {result.total_cost} / {budget}")
    print(f"    калорій:     {result.total_calories}")


def main() -> None:
    print("Каталог страв:")
    for name, info in ITEMS.items():
        ratio = info["calories"] / info["cost"]
        print(f"  {name:<10} вартість={info['cost']:<3}  калорій={info['calories']:<4}  кал/$ = {ratio:.2f}")
    print()

    for budget in (50, 80, 100, 150):
        print(f"=== Бюджет = {budget} ===")
        _print_result("Жадібний (greedy)", greedy_algorithm(ITEMS, budget), budget)
        _print_result("Динамічне (DP)   ", dynamic_programming(ITEMS, budget), budget)
        print()


if __name__ == "__main__":
    main()
