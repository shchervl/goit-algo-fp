"""Рекурсивна геометрія дерева Піфагора: гілки та квадрати.

Чистий модуль — імпортується без UI-залежностей.
"""

from __future__ import annotations

import math
from typing import Iterator

Point = tuple[float, float]
Branch = tuple[Point, Point, int]
Square = tuple[list[Point], int]

DEFAULT_ANGLE = math.radians(45)
DEFAULT_RATIO = 1 / math.sqrt(2)
TRUNK_ANGLE = math.pi / 2  # вертикально вгору


def generate_branches(
    depth: int,
    x: float = 0.0,
    y: float = 0.0,
    length: float = 1.0,
    angle: float = TRUNK_ANGLE,
    angle_split: float = DEFAULT_ANGLE,
    ratio: float = DEFAULT_RATIO,
) -> Iterator[Branch]:
    """Рекурсивно генерує гілки дерева як (start, end, remaining).

    depth=0 → лише стовбур. depth=n → 2^(n+1) − 1 гілок сумарно.
    """
    if depth < 0:
        return
    end = (x + length * math.cos(angle), y + length * math.sin(angle))
    yield (x, y), end, depth
    if depth == 0:
        return
    new_len = length * ratio
    yield from generate_branches(
        depth - 1, end[0], end[1], new_len, angle + angle_split, angle_split, ratio
    )
    yield from generate_branches(
        depth - 1, end[0], end[1], new_len, angle - angle_split, angle_split, ratio
    )


def square_corners(x: float, y: float, size: float, angle: float) -> list[Point]:
    """Чотири кути квадрата проти годинникової стрілки: [BL, BR, TR, TL]."""
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    return [
        (x, y),
        (x + size * cos_a, y + size * sin_a),
        (x + size * cos_a - size * sin_a, y + size * sin_a + size * cos_a),
        (x - size * sin_a, y + size * cos_a),
    ]


def generate_squares(
    depth: int,
    x: float = 0.0,
    y: float = 0.0,
    size: float = 1.0,
    angle: float = 0.0,
    angle_split: float = DEFAULT_ANGLE,
) -> Iterator[Square]:
    """Рекурсивно генерує квадрати дерева як (corners, remaining).

    Лівий нащадок: сторона = size·cos(α), кут = angle+α, нижній-лівий = TL батька.
    Правий нащадок: сторона = size·sin(α), кут = angle+α−π/2, нижній-лівий = вершина трикутника.
    """
    if depth < 0:
        return
    corners = square_corners(x, y, size, angle)
    yield corners, depth
    if depth == 0:
        return

    _bl, _br, _tr, top_left = corners
    left_angle = angle + angle_split
    left_size = size * math.cos(angle_split)
    apex = (
        top_left[0] + left_size * math.cos(left_angle),
        top_left[1] + left_size * math.sin(left_angle),
    )
    right_angle = angle + angle_split - math.pi / 2
    right_size = size * math.sin(angle_split)

    yield from generate_squares(
        depth - 1, top_left[0], top_left[1], left_size, left_angle, angle_split
    )
    yield from generate_squares(
        depth - 1, apex[0], apex[1], right_size, right_angle, angle_split
    )
