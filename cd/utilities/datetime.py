from __future__ import annotations

import datetime as dt
from collections.abc import Sequence

import humanize
import pendulum

from cd import enums


__all__ = (
    "convert_datetime",
    "format_datetime",
    "format_difference",
    "format_seconds"
)


def convert_datetime(
    _to_convert: dt.datetime | pendulum.DateTime,
    /
) -> pendulum.DateTime:

    if type(_to_convert) is dt.datetime and _to_convert.tzinfo is None:
        _to_convert = _to_convert.replace(tzinfo=dt.timezone.utc)

    return pendulum.instance(_to_convert)


def format_datetime(
    _to_format: dt.datetime | pendulum.DateTime | pendulum.Date | pendulum.Time,
    /, *,
    format: enums.DateTimeFormat,
) -> str:

    if isinstance(_to_format, dt.datetime):
        _to_format = convert_datetime(_to_format)

    return _to_format.format(format.value)


def format_difference(
    _datetime: dt.datetime | pendulum.DateTime,
    /, *,
    suppress: Sequence[str] = ("seconds",)
) -> str:

    datetime = convert_datetime(_datetime) if type(_datetime) is dt.datetime else _datetime
    assert isinstance(datetime, pendulum.DateTime)

    now: pendulum.DateTime = pendulum.now(tz=datetime.timezone).replace(microsecond=0)

    return humanize.precisedelta(now.diff(datetime), format="%0.0f", suppress=suppress)


def format_seconds(
    _seconds: float,
    /, *,
    friendly: bool = False
) -> str:

    _minutes, _seconds = divmod(round(_seconds), 60)
    _hours, _minutes = divmod(_minutes, 60)
    _days, _hours = divmod(_hours, 24)

    days, hours, minutes, seconds = round(_days), round(_hours), round(_minutes), round(_seconds)

    if friendly:
        return f"{f'{days}d ' if days else ''}" \
               f"{f'{hours}h ' if hours or days else ''}" \
               f"{minutes}m " \
               f"{seconds}s"

    return f"{f'{days:02d}:' if days else ''}" \
           f"{f'{hours:02d}:' if hours or days else ''}" \
           f"{minutes:02d}:" \
           f"{seconds:02d}"
