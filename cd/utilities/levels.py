import math


__all__ = (
    "level",
    "xp_needed_for_level",
)


def level(_xp: int, /) -> int:
    return math.floor((_xp / 50) ** (1 / 2.1))


def xp_needed_for_level(_level: int, /) -> int:
    return math.ceil((_level ** 2.1) * 50)
