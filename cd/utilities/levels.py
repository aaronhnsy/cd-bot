import math


__all__ = (
    "level",
    "xp_needed_for_level",
)


def level(_xp: int, /) -> int:
    return math.floor((((_xp / 100) ** (1.0 / 1.45)) / 3)) + 1


def xp_needed_for_level(_level: int, /) -> int:
    return 0 if _level <= 0 else math.ceil((((_level - 1) * 3) ** 1.45) * 100)
