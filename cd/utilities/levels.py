import math


__all__ = (
    "level",
    "needed_xp",
)


def level(_xp: int) -> int:
    return math.floor((((_xp / 100) ** (1.0 / 1.5)) / 3))


def needed_xp(_level: int, xp: int) -> int:
    return round((((((_level + 1) * 3) ** 1.5) * 100) - xp))
