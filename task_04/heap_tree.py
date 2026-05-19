"""Візуалізація бінарної купи як дерева через networkx + matplotlib.

Купа зберігається у вигляді масиву (так працює heapq у Python):
для вузла з індексом i його нащадки лежать на 2i+1 (лівий) та 2i+2 (правий).
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import networkx as nx

ColorFn = Callable[[int, Any], str]


def _default_color(_idx: int, _val: Any) -> str:
    return "skyblue"


class Node:
    """Вузол бінарного дерева з кольором і унікальним id для networkx."""

    def __init__(self, key: Any, color: str = "skyblue") -> None:
        self.left: Node | None = None
        self.right: Node | None = None
        self.val: Any = key
        self.color: str = color
        self.id: str = str(uuid.uuid4())


def _validate_min_heap(heap: list[Any]) -> None:
    """Перевіряє інваріант min-heap: батько <= кожна дитина."""
    for i, val in enumerate(heap):
        for child_idx in (2 * i + 1, 2 * i + 2):
            if child_idx < len(heap) and heap[child_idx] < val:
                raise ValueError(
                    f"не min-heap: heap[{i}]={val!r} > heap[{child_idx}]={heap[child_idx]!r}"
                )


def build_tree_from_heap(
    heap: list[Any],
    color_fn: ColorFn = _default_color,
    validate: bool = False,
) -> Node | None:
    """Створює дерево вузлів з масиву купи.

    heap[0] стає коренем; для кожного індексу i діти — heap[2i+1], heap[2i+2].
    Повертає None для порожньої купи.

    Args:
        heap: масив купи
        color_fn: (index, value) → колір; за замовч. всі вузли блакитні
        validate: якщо True, перевіряє min-heap інваріант, інакше довіряє caller-у
    """
    if not heap:
        return None
    if validate:
        _validate_min_heap(heap)
    nodes = [Node(value, color=color_fn(i, value)) for i, value in enumerate(heap)]
    for i, node in enumerate(nodes):
        left_idx = 2 * i + 1
        right_idx = 2 * i + 2
        if left_idx < len(nodes):
            node.left = nodes[left_idx]
        if right_idx < len(nodes):
            node.right = nodes[right_idx]
    return nodes[0]


def _build_graph(root: Node) -> nx.DiGraph:
    """Будує networkx DiGraph з вузлами (з мітками й кольорами) та ребрами."""
    graph = nx.DiGraph()

    def visit(node: Node) -> None:
        graph.add_node(node.id, color=node.color, label=node.val)
        for child in (node.left, node.right):
            if child is not None:
                graph.add_edge(node.id, child.id)
                visit(child)

    visit(root)
    return graph


def _luminance(color: str) -> float:
    """Перцептивна яскравість 0.0–1.0 за RGB (WCAG-наближення).

    Приймає hex (#rrggbb) або іменований колір matplotlib (skyblue тощо).
    """
    r, g, b = mcolors.to_rgb(color)
    return 0.299 * r + 0.587 * g + 0.114 * b


def _layout(root: Node) -> dict[str, tuple[float, float]]:
    """Розкладка дерева: листя рівномірно, батько = середина між дітьми.

    Уникає колапсу нижніх рівнів (як у `1/2^layer`), завдяки чому глибокі купи
    залишаються читабельними. Дерево центрується горизонтально навколо 0.
    """
    pos: dict[str, tuple[float, float]] = {}
    leaf_counter = [0]

    def visit(node: Node, depth: int) -> float:
        left_x = visit(node.left, depth + 1) if node.left is not None else None
        right_x = visit(node.right, depth + 1) if node.right is not None else None

        if left_x is None and right_x is None:
            x = float(leaf_counter[0])
            leaf_counter[0] += 1
        elif left_x is None:
            x = right_x  # type: ignore[assignment]
        elif right_x is None:
            x = left_x
        else:
            x = (left_x + right_x) / 2

        pos[node.id] = (x, float(-depth))
        return x

    visit(root, 0)

    # горизонтальне центрування
    xs = [p[0] for p in pos.values()]
    center = (max(xs) + min(xs)) / 2
    return {nid: (x - center, y) for nid, (x, y) in pos.items()}


def draw_tree(
    root: Node | None,
    title: str = "Бінарне дерево",
    save: str | None = None,
    node_labels: dict[str, str] | None = None,
) -> None:
    """Малює довільне бінарне дерево з кореня. Empty (None) — тихо нічого.

    Args:
        root: корінь дерева
        title: заголовок
        save: якщо вказано, зберігає у PNG
        node_labels: опц. словник node.id → мітка; інакше — node.val
    """
    if root is None:
        return

    graph = _build_graph(root)
    pos = _layout(root)

    colors = [data["color"] for _, data in graph.nodes(data=True)]
    if node_labels is None:
        labels = {nid: data["label"] for nid, data in graph.nodes(data=True)}
    else:
        labels = {
            nid: node_labels.get(nid, str(data["label"]))
            for nid, data in graph.nodes(data=True)
        }

    # адаптивні розміри під розмір дерева
    n = len(graph.nodes)
    levels = max(1, n.bit_length())
    bottom_width = 2 ** (levels - 1)
    fig_w = max(10.0, min(24.0, bottom_width * 0.8))
    fig_h = max(6.0, levels * 1.5)
    node_size = max(720, min(3600, 17280 // n))
    font_size = max(7, min(11, 90 // levels))

    fig = plt.figure(figsize=(fig_w, fig_h))
    plt.title(title)
    nx.draw_networkx_nodes(graph, pos, node_size=node_size, node_color=colors)
    nx.draw_networkx_edges(graph, pos, arrows=False)

    # Мітки з адаптивним кольором: світлий шрифт на темному фоні, темний на світлому
    LUMINANCE_THRESHOLD = 0.55
    dark_bg_labels, light_bg_labels = {}, {}
    for nid, data in graph.nodes(data=True):
        if _luminance(data["color"]) < LUMINANCE_THRESHOLD:
            dark_bg_labels[nid] = labels[nid]
        else:
            light_bg_labels[nid] = labels[nid]
    if dark_bg_labels:
        nx.draw_networkx_labels(
            graph, pos, labels=dark_bg_labels, font_size=font_size, font_color="white"
        )
    if light_bg_labels:
        nx.draw_networkx_labels(
            graph, pos, labels=light_bg_labels, font_size=font_size, font_color="black"
        )
    if save:
        fig.savefig(save, dpi=120, bbox_inches="tight")
    else:
        plt.show()
    plt.close(fig)


def draw_heap(
    heap: list[Any],
    title: str = "Бінарна купа",
    save: str | None = None,
    color_fn: ColorFn = _default_color,
    validate: bool = False,
) -> None:
    """Будує дерево з купи (масиву) та малює його.

    Args:
        heap: масив купи (як після heapq.heapify)
        title: заголовок вікна/файлу
        save: якщо вказано, зберігає у PNG замість показу
        color_fn: (index, value) → колір вузла
        validate: якщо True, перевіряє min-heap інваріант
    """
    root = build_tree_from_heap(heap, color_fn=color_fn, validate=validate)
    draw_tree(root, title=title, save=save)
