"""Кольори та товщина ліній за рівнем рекурсії — спільні для tk- та mpl-рендеру."""


def color_for(remaining: int, depth_max: int) -> str:
    """Градієнт коричневий (стовбур) → зелений (листя)."""
    t = 1.0 - (remaining / depth_max if depth_max > 0 else 0.0)
    r = int(round(101 * (1 - t) + 60 * t))
    g = int(round(67 * (1 - t) + 140 * t))
    b = int(round(33 * (1 - t) + 50 * t))
    return f"#{r:02x}{g:02x}{b:02x}"


def linewidth_for(remaining: int) -> float:
    return max(0.6, 0.5 + 0.6 * remaining)
