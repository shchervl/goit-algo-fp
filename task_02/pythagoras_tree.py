"""Tkinter UI дерева Піфагора: рідні Radiobutton + Scale + Canvas."""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk
from typing import Literal

from .geometry import DEFAULT_ANGLE, DEFAULT_RATIO, generate_branches, generate_squares
from .styling import color_for, linewidth_for

Mode = Literal["branches", "squares"]

PANEL_WIDTH = 260
GROUP_PADY = 8
CANVAS_PAD = 20
MIN_CANVAS_SIZE = 100
INITIAL_REDRAW_DELAY_MS = 50


def _draw_on_canvas(
    canvas: tk.Canvas,
    mode: Mode,
    depth: int,
    angle_split: float,
    ratio: float,
    base_length: float,
) -> None:
    """Малює дерево на tkinter Canvas з автомасштабуванням під поточний розмір."""
    canvas.delete("all")
    cw = max(canvas.winfo_width(), MIN_CANVAS_SIZE)
    ch = max(canvas.winfo_height(), MIN_CANVAS_SIZE)

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

    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    w, h = (maxx - minx) or 1.0, (maxy - miny) or 1.0
    scale = min((cw - 2 * CANVAS_PAD) / w, (ch - 2 * CANVAS_PAD) / h)
    ox = CANVAS_PAD + (cw - 2 * CANVAS_PAD - w * scale) / 2 - minx * scale
    oy = CANVAS_PAD + (ch - 2 * CANVAS_PAD - h * scale) / 2 + maxy * scale  # y перевернутий

    def tx(x: float) -> float:
        return ox + x * scale

    def ty(y: float) -> float:
        return oy - y * scale

    if mode == "branches":
        for start, end, remaining in items:
            canvas.create_line(
                tx(start[0]), ty(start[1]), tx(end[0]), ty(end[1]),
                fill=color_for(remaining, depth),
                width=max(1, round(linewidth_for(remaining))),
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
    initial_mode: Mode = "branches",
    ratio: float = DEFAULT_RATIO,
    base_length: float = 1.0,
    max_depth: int = 12,
) -> None:
    """Запускає tkinter-вікно з повзунками та радіо-перемикачем стилю."""
    root = tk.Tk()
    root.title("Дерево Піфагора")
    root.geometry("1100x880")
    root.minsize(900, 680)

    style = ttk.Style()
    style.configure("Value.TLabel", font=("", 12, "bold"))
    style.configure("Hint.TLabel", foreground="#777", font=("", 9))

    mode_var = tk.StringVar(value=initial_mode)

    # ── Бокова панель з фіксованою шириною ────────────────────────────────
    panel = ttk.Frame(root, padding=(12, 12, 8, 12), width=PANEL_WIDTH)
    panel.pack(side=tk.LEFT, fill=tk.Y)
    panel.pack_propagate(False)
    panel.columnconfigure(0, weight=1)

    # ── Група: Стиль ─────────────────────────────────────────────────────
    style_box = ttk.LabelFrame(panel, text=" Стиль ", padding=(10, 6))
    style_box.grid(row=0, column=0, sticky="ew", pady=(0, GROUP_PADY))
    ttk.Radiobutton(style_box, text="гілки", variable=mode_var, value="branches").pack(anchor="w", pady=2)
    ttk.Radiobutton(style_box, text="квадрати", variable=mode_var, value="squares").pack(anchor="w", pady=2)

    # ── Група: Параметри ─────────────────────────────────────────────────
    params_box = ttk.LabelFrame(panel, text=" Параметри ", padding=(10, 6))
    params_box.grid(row=1, column=0, sticky="ew", pady=(0, GROUP_PADY))
    params_box.columnconfigure(1, weight=1)

    ttk.Label(params_box, text="Рівень рекурсії").grid(row=0, column=0, sticky="w", pady=(4, 0))
    depth_value = ttk.Label(params_box, text=str(initial_depth), style="Value.TLabel")
    depth_value.grid(row=0, column=1, sticky="e", pady=(4, 0))
    depth_scale = ttk.Scale(
        params_box, from_=0, to=max_depth, orient=tk.HORIZONTAL,
        command=lambda v: depth_value.config(text=str(int(float(v)))),
    )
    depth_scale.set(initial_depth)
    depth_scale.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(2, 4))
    ttk.Label(params_box, text=f"0 — {max_depth}", style="Hint.TLabel").grid(
        row=2, column=0, columnspan=2, sticky="w", pady=(0, 8))

    ttk.Label(params_box, text="Кут розгалуження").grid(row=3, column=0, sticky="w")
    angle_value = ttk.Label(params_box, text=f"{int(initial_angle_deg)}°", style="Value.TLabel")
    angle_value.grid(row=3, column=1, sticky="e")
    angle_scale = ttk.Scale(
        params_box, from_=0, to=90, orient=tk.HORIZONTAL,
        command=lambda v: angle_value.config(text=f"{int(float(v))}°"),
    )
    angle_scale.set(initial_angle_deg)
    angle_scale.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(2, 4))
    ttk.Label(params_box, text="0° — 90° (45° канонічно)", style="Hint.TLabel").grid(
        row=5, column=0, columnspan=2, sticky="w")

    # ── Група: Інформація ────────────────────────────────────────────────
    info_box = ttk.LabelFrame(panel, text=" Інформація ", padding=(10, 6))
    info_box.grid(row=2, column=0, sticky="ew", pady=(0, GROUP_PADY))
    info_box.columnconfigure(1, weight=1)

    ttk.Label(info_box, text="Кількість:").grid(row=0, column=0, sticky="w", pady=2)
    count_value = ttk.Label(info_box, text="—", font=("", 10, "bold"))
    count_value.grid(row=0, column=1, sticky="e", pady=2)

    # ── Розділювач і canvas ──────────────────────────────────────────────
    ttk.Separator(root, orient="vertical").pack(side=tk.LEFT, fill=tk.Y)
    canvas = tk.Canvas(root, bg="white", highlightthickness=0)
    canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # ── Логіка оновлення ─────────────────────────────────────────────────
    def redraw(*_args) -> None:
        d = int(depth_scale.get())
        a = int(angle_scale.get())
        depth_value.config(text=str(d))
        angle_value.config(text=f"{a}°")
        mode: Mode = "branches" if mode_var.get() == "branches" else "squares"
        _draw_on_canvas(canvas, mode, d, math.radians(a), ratio, base_length)
        kind = "гілок" if mode == "branches" else "квадратів"
        count_value.config(text=f"{2 ** (d + 1) - 1} {kind}")

    depth_scale.bind("<ButtonRelease-1>", redraw)
    angle_scale.bind("<ButtonRelease-1>", redraw)
    mode_var.trace_add("write", lambda *_: redraw())
    canvas.bind("<Configure>", lambda _e: redraw())

    root.after(INITIAL_REDRAW_DELAY_MS, redraw)
    root.mainloop()
