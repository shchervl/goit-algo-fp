"""Демонстрація алгоритму Дейкстри на класичному графі з 6 вершин.

Запуск:
    uv run python -m task_03.demo
"""

from __future__ import annotations

import math

from task_03.dijkstra import dijkstra
from task_03.graph import Graph


def build_sample_graph() -> Graph:
    """Класичний приклад з Вікіпедії: 6 вершин, 9 ребер, неорієнтований."""
    edges = [
        ("A", "B", 7),
        ("A", "C", 9),
        ("A", "F", 14),
        ("B", "C", 10),
        ("B", "D", 15),
        ("C", "D", 11),
        ("C", "F", 2),
        ("D", "E", 6),
        ("E", "F", 9),
    ]
    g = Graph(directed=False)
    for u, v, w in edges:
        g.add_edge(u, v, w)
    return g


def print_shortest_paths(graph: Graph[str], start: str) -> None:
    result = dijkstra(graph, start)
    print(f"Граф: {graph!r}")
    print(f"Старт: {start}\n")
    print(f"{'Куди':<6} {'Відстань':<10} Шлях")
    print("-" * 40)
    for node in sorted(graph.nodes):
        d = result.distances.get(node, math.inf)
        path = result.path_to(node)
        path_str = " → ".join(path) if path else "—"
        d_str = f"{d:<10.1f}" if d != math.inf else f"{'∞':<10}"
        print(f"{node:<6} {d_str} {path_str}")


def main() -> None:
    graph = build_sample_graph()
    print_shortest_paths(graph, start="A")


if __name__ == "__main__":
    main()
