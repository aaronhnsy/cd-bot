# Standard Library
import datetime as dt
from typing import Literal, TypeAlias

# Libraries
import pendulum

# Project
from cd import enums


__all__ = [
    "convert_datetime",
    "format_date_and_or_time",
    "format_seconds",
]

PythonDateTime: TypeAlias = dt.datetime

PendulumDateTime: TypeAlias = pendulum.DateTime
PendulumDate: TypeAlias = pendulum.Date
PendulumTime: TypeAlias = pendulum.Time
PendulumDateAndOrTime: TypeAlias = PendulumDateTime | PendulumDate | PendulumTime


def convert_datetime(datetime: PythonDateTime) -> PendulumDateTime:
    datetime = datetime.replace(tzinfo=None)
    return pendulum.instance(datetime)


def format_date_and_or_time(
    date_and_or_time: PythonDateTime | PendulumDateAndOrTime,
    /, *,
    format: enums.DateTimeFormat,
    timezone_format: Literal["Z", "ZZ", "z", "zz"] | None = None
) -> str:
    fmt = format.value + (f" ({timezone_format})" if timezone_format else "")
    if isinstance(date_and_or_time, PendulumDateAndOrTime):
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
