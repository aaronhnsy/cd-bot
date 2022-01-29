# Future
from __future__ import annotations

# Packages
from discord.enums import Enum


__all__ = (
    "Environment",
    "DatetimeFormat",
    "LogType",
    "Filter",
    "EmbedSize"
)


class Environment(Enum):
    PRODUCTION = 0
    DEVELOPMENT = 1


class DatetimeFormat(Enum):

    # Dates
    FULL_LONG_DATE = "dddd [the] Do [of] MMMM YYYY"
    PARTIAL_LONG_DATE = "dddd Do [of] MMMM YYYY"
    LONG_DATE = "dddd Do MMMM YYYY"

    FULL_SHORT_DATE = "DD/MM/YYYY"
    PARTIAL_SHORT_DATE = "D/M/YY"

    FULL_COMPUTER_DATE = "YYYY/MM/DD"
    PARTIAL_COMPUTER_DATE = "YY/M/D"

    # Times
    FULL_TIME = "hh:mm:ss A"
    PARTIAL_TIME = "hh:mm A"

    # Dates and times
    FULL_LONG_DATETIME = "dddd [the] Do [of] MMMM YYYY [at] hh:mm A"
    FULL_LONG_DATETIME_WITH_SECONDS = "dddd [the] Do [of] MMMM YYYY [at] hh:mm:ss A"

    PARTIAL_LONG_DATETIME = "dddd Do [of] MMMM YYYY [at] hh:mm A"
    PARTIAL_LONG_DATETIME_WITH_SECONDS = "dddd Do [of] MMMM YYYY [at] hh:mm:ss A"

    SHORT_DATETIME = "dddd Do MMMM YYYY [at] hh:mm A"
    SHORT_DATETIME_WITH_SECONDS = "dddd Do MMMM YYYY [at] hh:mm:ss A"


class LogType(Enum):
    DM = 0
    GUILD = 1
    ERROR = 2
    COMMAND = 3


class Filter(Enum):
    ROTATION = "8D"
    NIGHTCORE = "Nightcore"
    MONO = "Mono"
    LEFT = "Left-ear"
    RIGHT = "Right-ear"


class EmbedSize(Enum):
    LARGE = 0
    MEDIUM = 1
    SMALL = 2
