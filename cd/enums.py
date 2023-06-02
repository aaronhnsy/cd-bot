import enum


__all__ = ["Environment"]


class Environment(enum.Enum):
    PRODUCTION = 0
    DEVELOPMENT = 1
