"""Алгоритм Дейкстри з бінарною купою (heapq) для пошуку найкоротших шляхів."""

from __future__ import annotations

import heapq
import math
from collections import deque
from collections.abc import Hashable
from typing import Generic, NamedTuple, TypeVar

from .graph import Graph

T = TypeVar("T", bound=Hashable)


class DijkstraResult(NamedTuple, Generic[T]):
    """Результат Дейкстри: відстані + дерево попередників.

    Підтримує tuple-unpacking (`distances, predecessors = result`) та
    attribute access (`result.distances`), а також `result.path_to(v)`.
    """

    distances: dict[T, float]
    predecessors: dict[T, T | None]

    def path_to(self, target: T) -> list[T]:
        return reconstruct_path(self.predecessors, target)


def dijkstra(graph: Graph[T], start: T) -> DijkstraResult[T]:
    """Найкоротші шляхи від start до всіх досяжних вершин.

    Використовує binary min-heap із lazy deletion: дублі залишаються у купі,
    але stale-записи (з ваги > поточної distances[u]) ігноруються при витяганні.
    Складність: O((V + E) log V).
    """
    if start not in graph:
        raise ValueError(f"вершина {start!r} відсутня у графі")

    distances: dict[T, float] = {start: 0.0}
    predecessors: dict[T, T | None] = {start: None}
    heap: list[tuple[float, T]] = [(0.0, start)]

    while heap:
        dist, u = heapq.heappop(heap)
        if dist > distances.get(u, math.inf):
            continue  # stale запис, нащадки вже оброблені з кращою вагою
        for v, weight in graph.neighbors(u):
            new_dist = dist + weight
            if new_dist < distances.get(v, math.inf):
                distances[v] = new_dist
                predecessors[v] = u
                heapq.heappush(heap, (new_dist, v))

    return DijkstraResult(distances, predecessors)


def reconstruct_path(predecessors: dict[T, T | None], target: T) -> list[T]:
    """Відновлює шлях від кореня до target за словником попередників.

    Повертає [] якщо target недосяжний.
    """
    if target not in predecessors:
        return []
    path: deque[T] = deque()
    cur: T | None = target
    while cur is not None:
        path.appendleft(cur)
        cur = predecessors[cur]
    return list(path)
