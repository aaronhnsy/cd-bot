# Future
from __future__ import annotations

# Standard Library
from typing import Type, TypeVar, overload


__all__ = (
    "Range",
)

NumberT = int | float
RangeT = TypeVar("RangeT", bound="Range")


class _RangeMeta(type):

    @overload
    def __getitem__(cls: Type[RangeT], max: int) -> Type[int]:
        ...

    @overload
    def __getitem__(cls: Type[RangeT], max: tuple[int, int]) -> Type[int]:
        ...

    @overload
    def __getitem__(cls: Type[RangeT], max: float) -> Type[float]:
        ...

    @overload
    def __getitem__(cls: Type[RangeT], max: tuple[float, float]) -> Type[float]:
        ...

    def __getitem__(cls, max):
        return cls(*max) if isinstance(max, tuple) else cls(None, max)


class Range(metaclass=_RangeMeta):

    def __init__(self, min: NumberT | None, max: NumberT) -> None:

        if min is not None and min >= max:
            raise ValueError("`min` value must be lower than `max`")

        self.min: NumberT | None = min
        self.max: NumberT = max
