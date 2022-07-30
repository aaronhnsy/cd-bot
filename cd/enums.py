from __future__ import annotations

from typing import TypeVar

from discord.enums import Enum

from cd import custom, exceptions, utilities


__all__ = (
    "Environment",
    "DateTimeFormat",
    "LogType",
    "Effect",
    "TrackEndReason",
    "Operation",
    "EmbedSize"
)

EnumType = TypeVar("EnumType", bound=Enum)


class Environment(Enum):
    Production = 0
    Development = 1


class DateTimeFormat(Enum):

    # Dates
    FullLongDate = "dddd [the] Do [of] MMMM YYYY"
    PartialLongDate = "dddd Do [of] MMMM YYYY"
    LongDate = "dddd Do MMMM YYYY"
    FullShortDate = "DD/MM/YYYY"
    PartialShortDate = "D/M/YY"
    FullComputerDate = "YYYY/MM/DD"
    PartialComputerDate = "YY/M/D"

    # Times
    FullTime = "hh:mm:ss A"
    PartialTime = "hh:mm A"

    # Dates and times
    FullLongDatetime = "dddd [the] Do [of] MMMM YYYY [at] hh:mm A"
    FullLongDatetimeWithSeconds = "dddd [the] Do [of] MMMM YYYY [at] hh:mm:ss A"
    PartialLongDatetime = "dddd Do [of] MMMM YYYY [at] hh:mm A"
    PartialLongDatetimeWithSeconds = "dddd Do [of] MMMM YYYY [at] hh:mm:ss A"
    ShortDatetime = "dddd Do MMMM YYYY [at] hh:mm A"
    ShortDatetimeWithSeconds = "dddd Do MMMM YYYY [at] hh:mm:ss A"


class LogType(Enum):
    Dm = 0
    Guild = 1
    Error = 2
    Command = 3


class Effect(Enum):
    Rotation = "8d"
    Nightcore = "nightcore"
    Mono = "mono"
    LeftEar = "left-ear"
    RightEar = "right-ear"


class TrackEndReason(Enum):
    Normal = 0
    Stuck = 1
    Exception = 2
    Replaced = 3


class Operation(Enum):
    Reset = 0
    Set = 1
    Add = 2
    Minus = 3


def convert_enum(
    cls: type[EnumType],
    name: str,
    argument: str
) -> EnumType:

    try:
        return cls[argument.replace(" ", "_").upper()]
    except KeyError:
        options = "\n".join(
            [f'- **{option.title()}**' for option in [enum.name.replace('_', ' ').lower() for enum in cls]]
        )
        raise exceptions.EmbedError(
            description=f"**{utilities.truncate(argument, 10)}** is not a valid {name}.\n\n"
                        f"Valid options are:\n"
                        f"{options}"
        )


class EmbedSize(Enum):
    Large = 0
    Medium = 1
    Small = 2
    Image = 3

    @classmethod
    async def convert(cls, _: custom.Context, argument: str) -> EmbedSize:
        return convert_enum(cls, "embed size", argument)
