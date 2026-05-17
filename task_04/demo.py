"""Демо: будує min-купу через heapq, потім візуалізує її як дерево.

Запуск:
    uv run python -m task_04.demo
"""

from __future__ import annotations

import heapq
import random

from task_04.heap_tree import draw_heap


def main() -> None:
    rng = random.Random(42)
    data = rng.sample(range(1, 100), 31)  # 31 унікальне значення; 5 повних рівнів
    heap = data.copy()
    heapq.heapify(heap)

    print(f"Вхідний масив ({len(data)}): {data}")
    print(f"Після heapify:               {heap}")
    print(f"Корінь min-купи (мінімум):    {heap[0]}")

    draw_heap(heap, title=f"Min-heap з {len(heap)} вузлів")


if __name__ == "__main__":
    main()
