"""CLI: запуск UI, статичний рендер, збереження у PNG."""

from __future__ import annotations

import argparse
import math

from .pythagoras_tree import run_ui
from .static_render import draw_tree


def _ask_depth() -> int:
    return int(input("Введіть рівень рекурсії (ціле число >= 0, напр. 8): ").strip())


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="task_02", description="Дерево Піфагора через рекурсію")
    parser.add_argument("-d", "--depth", type=int, default=None, help="рівень рекурсії (>=0)")
    parser.add_argument("-a", "--angle", type=float, default=45.0, help="кут розгалуження (0 < α < 90)")
    parser.add_argument("-r", "--ratio", type=float, default=1 / math.sqrt(2),
                        help="коеф. зменшення гілки (тільки для branches)")
    parser.add_argument("-l", "--length", type=float, default=1.0, help="довжина стовбура / сторона кореня")
    parser.add_argument("-m", "--mode", choices=("branches", "squares"), default="branches")
    parser.add_argument("--save", type=str, default=None, help="зберегти у PNG (без UI)")
    parser.add_argument("--no-ui", action="store_true", help="статичне matplotlib-вікно")
    args = parser.parse_args(argv)

    if not (0 < args.angle < 90):
        parser.error("angle має бути в межах (0, 90)")
    if not (0 < args.ratio < 1):
        parser.error("ratio має бути в (0, 1)")

    static = args.save or args.no_ui
    depth = args.depth if args.depth is not None else (_ask_depth() if static else 8)
    if depth < 0:
        parser.error("depth має бути >= 0")

    if static:
        draw_tree(depth, mode=args.mode, angle_split=math.radians(args.angle),
                  ratio=args.ratio, length=args.length, save=args.save)
    else:
        run_ui(
            initial_depth=depth,
            initial_angle_deg=args.angle,
            initial_mode=args.mode,
            ratio=args.ratio,
            base_length=args.length,
        )


if __name__ == "__main__":
    main()
