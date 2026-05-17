"""Tkinter UI дерева Піфагора: рідні Radiobutton + Scale + Canvas."""

from __future__ import annotations

import math

from .geometry import generate_branches, generate_squares
from .styling import color_for, linewidth_for


def _draw_on_canvas(
    canvas,
    mode: str,
    depth: int,
    angle_split: float,
    ratio: float,
    base_length: float,
) -> None:
    """Малює дерево на tkinter Canvas з автомасштабуванням під поточний розмір."""
    canvas.delete("all")
    cw = max(canvas.winfo_width(), 100)
    ch = max(canvas.winfo_height(), 100)

    if mode == "branches":
        items = list(generate_branches(
            depth, length=base_length, angle_split=angle_split, ratio=ratio
        ))
        xs = [p[0] for s, e, _ in items for p in (s, e)]
        ys = [p[1] for s, e, _ in items for p in (s, e)]
    else:
        items = list(generate_squares(depth, size=base_length, angle_split=angle_split))
        xs = [p[0] for corners, _ in items for p in corners]
        ys = [p[1] for corners, _ in items for p in corners]

    pad = 20
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    w, h = (maxx - minx) or 1.0, (maxy - miny) or 1.0
    scale = min((cw - 2 * pad) / w, (ch - 2 * pad) / h)
    ox = pad + (cw - 2 * pad - w * scale) / 2 - minx * scale
    oy = pad + (ch - 2 * pad - h * scale) / 2 + maxy * scale  # y перевернутий

    def tx(x: float) -> float:
        return ox + x * scale

    def ty(y: float) -> float:
        return oy - y * scale

    if mode == "branches":
        for start, end, remaining in items:
            canvas.create_line(
                tx(start[0]), ty(start[1]), tx(end[0]), ty(end[1]),
                fill=color_for(remaining, depth),
                width=max(1, int(round(linewidth_for(remaining)))),
                capstyle="round",
            )
    else:
        for corners, remaining in items:
            flat: list[float] = []
            for px, py in corners:
                flat.extend([tx(px), ty(py)])
            canvas.create_polygon(
                *flat, fill=color_for(remaining, depth), outline="black", width=1,
            )


def run_ui(
    initial_depth: int = 8,
    initial_angle_deg: float = 45.0,
    initial_mode: str = "branches",
    ratio: float = 1 / math.sqrt(2),
    base_length: float = 1.0,
    max_depth: int = 12,
) -> None:
    """Запускає tkinter-вікно з повзунками та радіо-кнопками."""
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("Дерево Піфагора")
    root.geometry("1000x900")

    mode_var = tk.StringVar(value=initial_mode)

    controls = ttk.Frame(root, padding=12)
    controls.pack(side=tk.LEFT, fill=tk.Y)

    ttk.Label(controls, text="Стиль", font=("", 11, "bold")).pack(anchor="w", pady=(0, 4))
    ttk.Radiobutton(controls, text="гілки", variable=mode_var, value="branches").pack(anchor="w")
    ttk.Radiobutton(controls, text="квадрати", variable=mode_var, value="squares").pack(anchor="w")

    ttk.Separator(controls).pack(fill=tk.X, pady=10)

    ttk.Label(controls, text="Рівень рекурсії", font=("", 11, "bold")).pack(anchor="w")
    depth_label = ttk.Label(controls, text=str(initial_depth))
    depth_label.pack(anchor="w")
    depth_scale = ttk.Scale(
        controls, from_=0, to=max_depth, orient=tk.HORIZONTAL, length=200,
        command=lambda v: depth_label.config(text=str(int(float(v)))),
    )
    depth_scale.set(initial_depth)
    depth_scale.pack(anchor="w", pady=(0, 8))

    ttk.Label(controls, text="Кут (°)", font=("", 11, "bold")).pack(anchor="w")
    angle_label = ttk.Label(controls, text=str(int(initial_angle_deg)))
    angle_label.pack(anchor="w")
    angle_scale = ttk.Scale(
        controls, from_=5, to=85, orient=tk.HORIZONTAL, length=200,
        command=lambda v: angle_label.config(text=str(int(float(v)))),
    )
    angle_scale.set(initial_angle_deg)
    angle_scale.pack(anchor="w", pady=(0, 8))

    info = ttk.Label(controls, text="", foreground="#555")
    info.pack(anchor="w", pady=(10, 0))

    canvas = tk.Canvas(root, bg="white", highlightthickness=0)
    canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def redraw(*_args) -> None:
        d = int(depth_scale.get())
        a = int(angle_scale.get())
        depth_label.config(text=str(d))
        angle_label.config(text=str(a))
        _draw_on_canvas(canvas, mode_var.get(), d, math.radians(a), ratio, base_length)
        kind = "гілок" if mode_var.get() == "branches" else "квадратів"
        info.config(text=f"{2 ** (d + 1) - 1} {kind}")

    depth_scale.bind("<ButtonRelease-1>", redraw)
    angle_scale.bind("<ButtonRelease-1>", redraw)
    mode_var.trace_add("write", lambda *_: redraw())
    canvas.bind("<Configure>", lambda _e: redraw())

    root.after(50, redraw)
    root.mainloop()
