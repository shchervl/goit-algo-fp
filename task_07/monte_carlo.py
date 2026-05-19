"""Метод Монте-Карло: оцінка ймовірностей сум при киданні двох кубиків.

Дві кістки 1–6 дають суму s ∈ [2, 12]. Аналітично кількість способів отримати
суму s = 6 − |s − 7|; ймовірність = ways(s) / 36. Емпірично — лічимо суми за
N кидків і ділимо на N. Згідно з законом великих чисел, при N → ∞ емпіричні
ймовірності збігаються до аналітичних.
"""

from __future__ import annotations

import random
from collections import Counter

SUM_RANGE = range(2, 13)  # можливі суми двох d6


def roll_pair(rng: random.Random) -> int:
    """Кидає дві кістки, повертає суму (2–12)."""
    return rng.randint(1, 6) + rng.randint(1, 6)


def simulate(n_rolls: int, seed: int | None = None) -> Counter[int]:
    """Виконує n_rolls кидків двох кубиків, повертає лічильник сум."""
    if n_rolls < 0:
        raise ValueError(f"n_rolls має бути ≥ 0, отримано {n_rolls}")
    rng = random.Random(seed)
    counts: Counter[int] = Counter()
    for _ in range(n_rolls):
        counts[roll_pair(rng)] += 1
    return counts


def empirical_probabilities(counts: Counter[int]) -> dict[int, float]:
    """З лічильника сум → словник {сума: ймовірність}. Порожні counts → нульові."""
    total = sum(counts.values())
    if total == 0:
        return {s: 0.0 for s in SUM_RANGE}
    return {s: counts.get(s, 0) / total for s in SUM_RANGE}


def analytical_probabilities() -> dict[int, float]:
    """Точні ймовірності: P(s) = (6 − |s − 7|) / 36."""
    return {s: (6 - abs(s - 7)) / 36 for s in SUM_RANGE}


def comparison_table(
    empirical: dict[int, float], analytical: dict[int, float]
) -> str:
    """Формує текстову таблицю порівняння: емпірична, аналітична, різниця."""
    lines = [
        f"{'Сума':<6} {'Емпірична':<14} {'Аналітична':<14} {'Δ':<10}",
        "-" * 50,
    ]
    for s in SUM_RANGE:
        e_pct = empirical[s] * 100
        a_pct = analytical[s] * 100
        delta = e_pct - a_pct
        lines.append(f"{s:<6} {e_pct:>6.2f}%        {a_pct:>6.2f}%        {delta:+.2f}%")
    return "\n".join(lines)


def plot_comparison(
    empirical: dict[int, float],
    analytical: dict[int, float],
    title: str = "Монте-Карло vs аналітика",
    save: str | None = None,
) -> None:
    """Bar-chart: емпіричні та аналітичні ймовірності поруч для кожної суми."""
    import matplotlib.pyplot as plt

    sums = list(SUM_RANGE)
    emp = [empirical[s] * 100 for s in sums]
    ana = [analytical[s] * 100 for s in sums]

    fig, ax = plt.subplots(figsize=(11, 6))
    width = 0.4
    x_emp = [s - width / 2 for s in sums]
    x_ana = [s + width / 2 for s in sums]
    ax.bar(x_emp, emp, width=width, label="Емпірична (Monte Carlo)", color="#4a90d9")
    ax.bar(x_ana, ana, width=width, label="Аналітична", color="#d97a4a")

    ax.set_xticks(sums)
    ax.set_xlabel("Сума на двох кубиках")
    ax.set_ylabel("Ймовірність, %")
    ax.set_title(title)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    if save:
        fig.savefig(save, dpi=120, bbox_inches="tight")
    else:
        plt.show()
    plt.close(fig)
