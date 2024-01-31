import datetime as dt
from typing import Literal

import pendulum

from cd import enums


__all__ = [
    "convert_datetime",
    "format_date_and_or_time",
    "format_seconds",
]


def convert_datetime(datetime: dt.datetime) -> pendulum.DateTime:
    datetime = datetime.replace(tzinfo=None)
    return pendulum.instance(datetime)


def format_date_and_or_time(
    date_and_or_time: dt.datetime | pendulum.Date | pendulum.Time | pendulum.DateTime,
    /, *,
    format: enums.DateTimeFormat,
    timezone_format: Literal["Z", "ZZ", "z", "zz"] | None = None
) -> str:
    fmt = format.value + (f" ({timezone_format})" if timezone_format else "")
    if isinstance(date_and_or_time, pendulum.Date | pendulum.Time | pendulum.DateTime):
        return date_and_or_time.format(fmt)
    return convert_datetime(date_and_or_time).format(fmt)


def format_seconds(seconds: int | float) -> str:
    if seconds < 1:
        return f"{seconds:.2f}ms"
    duration = pendulum.duration(seconds=seconds)
    parts: list[tuple[str, float]] = [
        ("y", duration.years),
        ("m", duration.months),
        ("w", duration.weeks),
        ("d", duration.remaining_days),
        ("h", duration.hours),
        ("m", duration.minutes),
        ("s", duration.remaining_seconds),
    ]
    return " ".join(f"{value}{unit}" for unit, value in parts if value > 0)
