# Future
from __future__ import annotations

# Standard Library
import datetime as dt
from collections.abc import Sequence

# Packages
import humanize
import pendulum

# My stuff
from utilities import enums


__all__ = (
    "convert_datetime",
    "format_datetime",
    "format_difference",
    "format_seconds"
)


def convert_datetime(
    datetime: dt.datetime | pendulum.DateTime, /
) -> pendulum.DateTime:

    datetime.replace(microsecond=0)

    if type(datetime) is dt.datetime and datetime.tzinfo == dt.timezone.utc:
        datetime = datetime.replace(tzinfo=None)

    return pendulum.instance(datetime, tz="UTC")


def format_datetime(
    datetime: dt.datetime | pendulum.DateTime | pendulum.Date | pendulum.Time, /,
    *, format: enums.DatetimeFormat,
) -> str:

    if isinstance(datetime, dt.datetime):
        datetime = convert_datetime(datetime)

    return datetime.format(format.value)


def format_difference(
    datetime: dt.datetime | pendulum.DateTime, /,
    *, suppress: Sequence[str] = ("seconds",)
) -> str:

    datetime = convert_datetime(datetime)

    # pendulum typings are a big wrong :)
    now = pendulum.now(tz=datetime.timezone).replace(microsecond=0)  # type: ignore

    # noinspection PyUnresolvedReferences
    return humanize.precisedelta(now.diff(datetime), format="%0.0f", suppress=suppress)


def format_seconds(
    seconds: float, /,
    *, friendly: bool = False
) -> str:

    seconds = round(seconds)
    minute, second = divmod(seconds, 60)
    hour, minute = divmod(minute, 60)
    day, hour = divmod(hour, 24)

    days, hours, minutes, seconds = round(day), round(hour), round(minute), round(second)

    if friendly:
        return f"{f'{days}d ' if days != 0 else ''}{f'{hours}h ' if hours != 0 or days != 0 else ''}{minutes}m {seconds}s"

    return f"{f'{days:02d}:' if days != 0 else ''}{f'{hours:02d}:' if hours != 0 or days != 0 else ''}{minutes:02d}:{seconds:02d}"
