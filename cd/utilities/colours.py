from __future__ import annotations

import colorsys


__all__ = (
    "darken_colour",
    "lighten_colour"
)


def darken_colour(red: float, green: float, blue: float, factor: float = 0.1) -> tuple[float, float, float]:
    h, l, s = colorsys.rgb_to_hls(red / 255.0, green / 255.0, blue / 255.0)
    red, green, blue = colorsys.hls_to_rgb(h, max(min(l * (1 - factor), 1.0), 0.0), s)
    return int(red * 255), int(green * 255), int(blue * 255)


def lighten_colour(red: float, green: float, blue: float, factor: float = 0.1) -> tuple[float, float, float]:
    h, l, s = colorsys.rgb_to_hls(red / 255.0, green / 255.0, blue / 255.0)
    red, green, blue = colorsys.hls_to_rgb(h, max(min(l * (1 + factor), 1.0), 0.0), s)
    return int(red * 255), int(green * 255), int(blue * 255)
