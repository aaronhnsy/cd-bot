# Libraries
import pendulum


__all__ = ["format_seconds"]


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
