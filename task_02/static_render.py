"""Статичний matplotlib-рендер дерева для --save / --no-ui."""

from __future__ import annotations

import math

from .geometry import Point, generate_branches, generate_squares
from .styling import color_for, linewidth_for


def _render_branches_mpl(ax, depth: int, angle_split: float, ratio: float, length: float) -> None:
    from matplotlib.collections import LineCollection

    ax.clear()
    ax.set_aspect("equal")
    ax.axis("off")

    by_depth: dict[int, list[tuple[Point, Point]]] = {}
    for start, end, remaining in generate_branches(
        depth, length=length, angle_split=angle_split, ratio=ratio
    ):
        by_depth.setdefault(remaining, []).append((start, end))

    for remaining, segments in by_depth.items():
        ax.add_collection(LineCollection(
            segments,
            colors=color_for(remaining, depth),
            linewidths=linewidth_for(remaining),
            capstyle="round",
        ))
    ax.autoscale_view()


def _render_squares_mpl(ax, depth: int, angle_split: float, length: float) -> None:
    from matplotlib.collections import PolyCollection

    ax.clear()
    ax.set_aspect("equal")
    ax.axis("off")

    by_depth: dict[int, list[list[Point]]] = {}
    for corners, remaining in generate_squares(depth, size=length, angle_split=angle_split):
        by_depth.setdefault(remaining, []).append(corners)

    for remaining, polys in by_depth.items():
        ax.add_collection(PolyCollection(
            polys,
            facecolors=color_for(remaining, depth),
            edgecolors="black",
            linewidths=0.4,
        ))
    ax.autoscale_view()


def draw_tree(
    depth: int,
    mode: str = "branches",
    angle_split: float = math.radians(45),
    ratio: float = 1 / math.sqrt(2),
    length: float = 1.0,
    save: str | None = None,
) -> None:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 10))
    if mode == "branches":
        _render_branches_mpl(ax, depth, angle_split, ratio, length)
    elif mode == "squares":
        _render_squares_mpl(ax, depth, angle_split, length)
    else:
        raise ValueError(f"невідомий mode={mode!r}; очікую 'branches' або 'squares'")
    fig.suptitle(f"Дерево Піфагора — {mode}, глибина {depth}", fontsize=12)

    if save:
        fig.savefig(save, dpi=120, bbox_inches="tight")
        print(f"Збережено у {save}")
    else:
        plt.show()
    plt.close(fig)
