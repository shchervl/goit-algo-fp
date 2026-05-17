"""Кольори та товщина ліній за рівнем рекурсії."""

TRUNK_RGB = (101, 67, 33)   # коричневий — біля кореня
LEAF_RGB = (60, 140, 50)    # зелений — на листі

MIN_LINEWIDTH = 0.6
LINEWIDTH_BASE = 0.5
LINEWIDTH_PER_LEVEL = 0.6


def color_for(remaining: int, depth_max: int) -> str:
    """Інтерполяція коричневий (стовбур) → зелений (листя)."""
    t = 1.0 - (remaining / depth_max if depth_max > 0 else 0.0)
    r, g, b = (round((1 - t) * a + t * c) for a, c in zip(TRUNK_RGB, LEAF_RGB))
    return f"#{r:02x}{g:02x}{b:02x}"


def linewidth_for(remaining: int) -> float:
    return max(MIN_LINEWIDTH, LINEWIDTH_BASE + LINEWIDTH_PER_LEVEL * remaining)
