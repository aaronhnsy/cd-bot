from __future__ import annotations

import re

from discord.ext import commands

from cd import custom, exceptions


__all__ = (
    "TimeConverter",
)

COLON_FORMAT_REGEX = re.compile(
    r"""
    ^
        (?:
            (?:
                (?P<hours>[0-1]?[0-9]|2[0-3]):
            )?
            (?P<minutes>[0-5]?[0-9]):
        )?
        (?P<seconds>[0-5]?[0-9])
    $
    """,
    flags=re.VERBOSE
)

HUMAN_FORMAT_REGEX = re.compile(
    r"""
    ^
        (?: (?P<hours>[0-1]?[0-9]|2[0-3]) \s? (?:h|hour|hours)              (?:\s?|\s?and\s?) )?
        (?: (?P<minutes>[0-5]?[0-9])      \s? (?:m|min|mins|minute|minutes) (?:\s?|\s?and\s?) )?
        (?: (?P<seconds>[0-5]?[0-9])      \s? (?:s|sec|secs|second|seconds)                   )?
    $
    """,
    flags=re.VERBOSE
)


class TimeConverter(commands.Converter[int]):

    async def convert(
        self,
        ctx: custom.Context,
        argument: str
    ) -> int:  # pyright: reportIncompatibleMethodOverride=false

        if (match := COLON_FORMAT_REGEX.match(argument)) or (match := HUMAN_FORMAT_REGEX.match(argument)):

            seconds = 0

            if _hours := match.group("hours"):
                seconds += int(_hours) * 60 * 60
            if _minutes := match.group("minutes"):
                seconds += int(_minutes) * 60
            if _seconds := match.group("seconds"):
                seconds += int(_seconds)

        else:

            try:
                seconds = int(argument)
            except ValueError as e:
                raise exceptions.EmbedError(description="That time format was not recognized.") from e

        return seconds
