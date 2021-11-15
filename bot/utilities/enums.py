# Future
from __future__ import annotations

# Packages
from discord.enums import Enum


__all__ = (
    "Environment",
    "DatetimeFormat"
)


class Environment(Enum):
    PRODUCTION = 0
    DEVELOPMENT = 1


class DatetimeFormat(Enum):
    FULL_LONG_DATE = "dddd [the] Do [of] MMMM YYYY"
    PARTIAL_LONG_DATE = "dddd Do [of] MMMM YYYY"
    LONG_DATE = "dddd Do MMMM YYYY"

    FULL_SHORT_DATE = "DD/MM/YYYY"
    PARTIAL_SHORT_DATE = "D/M/YY"

    FULL_COMPUTER_DATE = "YYYY/MM/DD"
    PARTIAL_COMPUTER_DATE = "YY/M/D"

    FULL_TIME = "hh:mm:ss"
    PARTIAL_TIME = "hh:mm"

    FULL_LONG_DATETIME = "dddd [the] Do [of] MMMM YYYY [at] hh:mm A"
    FULL_LONG_DATETIME_WITH_SECONDS = "dddd [the] Do [of] MMMM YYYY [at] hh:mm:ss A"

    PARTIAL_LONG_DATETIME = "dddd Do [of] MMMM YYYY [at] hh:mm A"
    PARTIAL_LONG_DATETIME_WITH_SECONDS = "dddd Do [of] MMMM YYYY [at] hh:mm:ss A"

    LONG_DATETIME = "dddd Do MMMM YYYY [at] hh:mm A"
    LONG_DATETIME_WITH_SECONDS = "dddd Do MMMM YYYY [at] hh:mm:ss A"


class LogType(Enum):
    DM = 0
    GUILD = 1
    ERROR = 2


class Filter(Enum):
    ROTATION = 0
    NIGHTCORE = 1
    MONO = 2
    LEFT = 3
    RIGHT = 4
