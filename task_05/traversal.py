"""Ітеративні обходи DFS/BFS бінарного дерева з кольоровою візуалізацією.

За завданням: DFS — через стек, BFS — через чергу, **без рекурсії**.
Кольори вузлів інтерполюються від темного до світлого відтінку синього
(приклад #1296F0) відповідно до порядку відвідування.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from typing import Literal

from task_04.heap_tree import Node, draw_tree

Order = Literal["dfs", "bfs"]
Traversal = Callable[[Node | None], list[Node]]

# Темний → світлий синій градієнт (центрований навколо прикладу #1296F0)
DARK_RGB = (5, 30, 80)
LIGHT_RGB = (210, 230, 250)
DEFAULT_COLOR = "skyblue"


def dfs_iterative(root: Node | None) -> list[Node]:
    """Обхід у глибину через стек (pre-order: корінь → ліве → праве).

    Праве дитя кладемо у стек першим, щоб ліве витяглось раніше.
    """
    if root is None:
        return []
    visited: list[Node] = []
    stack: list[Node] = [root]
    while stack:
        node = stack.pop()
        visited.append(node)
        if node.right is not None:
            stack.append(node.right)
        if node.left is not None:
            stack.append(node.left)
    return visited


def bfs_iterative(root: Node | None) -> list[Node]:
    """Обхід у ширину через FIFO-чергу (рівень за рівнем)."""
    if root is None:
        return []
    visited: list[Node] = []
    queue: deque[Node] = deque([root])
    while queue:
        node = queue.popleft()
        visited.append(node)
        if node.left is not None:
            queue.append(node.left)
        if node.right is not None:
            queue.append(node.right)
    return visited


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"


def shade_gradient(
    n: int,
    dark: tuple[int, int, int] = DARK_RGB,
    light: tuple[int, int, int] = LIGHT_RGB,
) -> list[str]:
    """Генерує n hex-кольорів від темного до світлого (лінійна інтерполяція в RGB).

    n=0 → []; n=1 → [темний]; n≥2 → рівномірний градієнт.
    """
    if n <= 0:
        return []
    denom = max(1, n - 1)
    return [
        _rgb_to_hex(tuple(round(d + (l - d) * i / denom) for d, l in zip(dark, light)))  # type: ignore[arg-type]
        for i in range(n)
    ]


def apply_traversal_colors(sequence: list[Node]) -> None:
    """Розфарбовує вузли in-place за порядком обходу: перший = темний, останній = світлий."""
    for node, color in zip(sequence, shade_gradient(len(sequence))):
        node.color = color


def reset_colors(root: Node | None, color: str = DEFAULT_COLOR) -> None:
    """Скидає колір усіх вузлів дерева на єдиний (за замовч. — skyblue)."""
    for node in dfs_iterative(root):
        node.color = color


TRAVERSALS: dict[Order, Traversal] = {
    "dfs": dfs_iterative,
    "bfs": bfs_iterative,
}

_TITLE_LABELS: dict[Order, str] = {
    "dfs": "DFS (стек)",
    "bfs": "BFS (черга)",
}


def draw_traversal(
    root: Node | None,
    order: Order = "dfs",
    save: str | None = None,
) -> list[Node]:
    """Обходить дерево та малює, фарбуючи вузли від темного до світлого.

    Повертає послідовність відвіданих вузлів.
    """
    if order not in TRAVERSALS:
        raise ValueError(f"невідомий order={order!r}; очікую {list(TRAVERSALS)}")
    sequence = TRAVERSALS[order](root)

    apply_traversal_colors(sequence)
    step_labels = {node.id: f"{i + 1}" for i, node in enumerate(sequence)}
    title = f"Обхід дерева: {_TITLE_LABELS[order]} — {len(sequence)} вузлів"
    draw_tree(root, title=title, save=save, node_labels=step_labels)
    return sequence
