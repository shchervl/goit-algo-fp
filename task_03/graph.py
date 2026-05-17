"""Зважений граф через список суміжності — для алгоритму Дейкстри."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Hashable, KeysView
from typing import Generic, TypeVar

T = TypeVar("T", bound=Hashable)


class Graph(Generic[T]):
    """Зважений граф; за замовчуванням неорієнтований.

    Список суміжності: для кожної вершини зберігаємо `[(сусід, вага), ...]`.
    Дозволяє кратні ребра та петлі.
    """

    def __init__(self, directed: bool = False) -> None:
        self._adj: dict[T, list[tuple[T, float]]] = defaultdict(list)
        self.directed = directed

    def add_node(self, node: T) -> None:
        """Реєструє ізольовану вершину без ребер."""
        _ = self._adj[node]

    def add_edge(self, u: T, v: T, weight: float = 1.0) -> None:
        """Додає ребро з вагою. Без аргументу `weight` — незважене (вага 1.0).

        `bool` навмисно відкидається: True/False як вага — майже завжди баг
        (формально bool — підклас int, тож без явної перевірки пройшло б).
        """
        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            raise TypeError(f"вага має бути числом, отримано {type(weight).__name__}")
        if weight < 0:
            raise ValueError(f"Дейкстра не приймає від'ємних ваг, отримано {weight}")
        self._adj[u].append((v, weight))
        if self.directed:
            self.add_node(v)
        else:
            self._adj[v].append((u, weight))

    def neighbors(self, u: T) -> list[tuple[T, float]]:
        return list(self._adj.get(u, ()))

    @property
    def nodes(self) -> KeysView[T]:
        return self._adj.keys()

    def __contains__(self, node: object) -> bool:
        return node in self._adj

    def __len__(self) -> int:
        return len(self._adj)

    def __repr__(self) -> str:
        kind = "directed" if self.directed else "undirected"
        return f"Graph({kind}, {len(self)} nodes)"
