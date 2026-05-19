"""Демо: візуалізує DFS та BFS обходи бінарного дерева.

Запуск:
    uv run python -m task_05.demo
"""

from __future__ import annotations

from task_04.heap_tree import Node, build_tree_from_heap
from task_05.traversal import draw_traversal


def build_sample_tree() -> Node:
    """Повне бінарне дерево з 31 вузла (5 рівнів)."""
    root = build_tree_from_heap(list(range(1, 32)))
    assert root is not None
    return root


def main() -> None:
    print("=== DFS (depth-first, через стек) ===")
    seq = draw_traversal(build_sample_tree(), order="dfs")
    print("Кроків:", len(seq))

    print()
    print("=== BFS (breadth-first, через чергу) ===")
    seq = draw_traversal(build_sample_tree(), order="bfs")
    print("Кроків:", len(seq))


if __name__ == "__main__":
    main()
