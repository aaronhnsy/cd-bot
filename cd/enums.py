# Standard Library
import enum


__all__ = [
    "Environment",
    "DateTimeFormat",
]


class Environment(enum.Enum):
    PRODUCTION = 0
    DEVELOPMENT = 1


class DateTimeFormat(enum.Enum):
    # Dates
    DATE = "dddd[,] Do MMMM YYYY"
    SHORT_DATE = "ddd[,] Do MMM YYYY"
    SHORTEST_DATE = "ddd[,] D MMM YYYY"
    # Numerical dates
    NUMERICAL_DATE = "DD/MM/YYYY"
    SHORT_NUMERICAL_DATE = "DD/MM/YY"
    SHORTEST_NUMERICAL_DATE = "D/M/YY"
    # Computer dates
    COMPUTER_DATE = "YYYY/MM/DD"
    SHORT_COMPUTER_DATE = "YY/MM/DD"
    SHORTEST_COMPUTER_DATE = "YY/M/D"

    # 24 hour time
    TIME = "HH:mm"
    TIME_WITH_SECONDS = "HH:mm:ss"
    # 12 hour time
    SIMPLE_TIME = "hh:mm A"
    SIMPLE_TIME_WITH_SECONDS = "hh:mm:ss A"

    # Date + 24 hour time
    DATE_WITH_TIME = "dddd[,] Do MMMM YYYY [at] HH:mm"
    DATE_WITH_TIME_AND_SECONDS = "dddd[,] Do MMMM YYYY [at] HH:mm:ss"
    SHORT_DATE_WITH_TIME = "ddd[,] Do MMM YYYY [at] HH:mm"
    SHORT_DATE_WITH_TIME_AND_SECONDS = "ddd[,] Do MMM YYYY [at] HH:mm:ss"
    SHORTEST_DATE_WITH_TIME = "ddd[,] D MMM YYYY [at] HH:mm"
    SHORTEST_DATE_WITH_TIME_AND_SECONDS = "ddd[,] D MMM YYYY [at] HH:mm:ss"
    # Date + 12 hour time
    DATE_WITH_SIMPLE_TIME = "dddd[,] Do MMMM YYYY [at] hh:mm A"
    DATE_WITH_SIMPLE_TIME_AND_SECONDS = "dddd[,] Do MMMM YYYY [at] hh:mm:ss A"
    SHORT_DATE_WITH_SIMPLE_TIME = "ddd[,] Do MMM YYYY [at] hh:mm A"
    SHORT_DATE_WITH_SIMPLE_TIME_AND_SECONDS = "ddd[,] Do MMM YYYY [at] hh:mm:ss A"
    SHORTEST_DATE_WITH_SIMPLE_TIME = "ddd[,] D MMM YYYY [at] hh:mm A"
    SHORTEST_DATE_WITH_SIMPLE_TIME_AND_SECONDS = "ddd[,] D MMM YYYY [at] hh:mm:ss A"
