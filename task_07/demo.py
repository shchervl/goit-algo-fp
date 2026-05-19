"""Демо: Монте-Карло симуляція для двох кубиків з порівнянням до аналітики.

Запуск:
    uv run python -m task_07.demo
"""

from __future__ import annotations

from task_07.monte_carlo import (
    analytical_probabilities,
    comparison_table,
    empirical_probabilities,
    plot_comparison,
    simulate,
)


def main() -> None:
    n_rolls = 100_000
    seed = 42

    print(f"Запускаю Монте-Карло: {n_rolls:,} кидків (seed={seed})\n")

    counts = simulate(n_rolls, seed=seed)
    empirical = empirical_probabilities(counts)
    analytical = analytical_probabilities()

    print(comparison_table(empirical, analytical))
    print()
    max_delta = max(abs(empirical[s] - analytical[s]) for s in empirical) * 100
    print(f"Максимальне відхилення: {max_delta:.2f}%")

    plot_comparison(
        empirical,
        analytical,
        title=f"Монте-Карло vs аналітика — {n_rolls:,} кидків",
    )


if __name__ == "__main__":
    main()
