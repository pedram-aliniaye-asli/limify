from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class Rate:
    limit: int
    period_seconds: int


_UNIT_SECONDS = {
    "second": 1,
    "seconds": 1,
    "sec": 1,
    "s": 1,
    "minute": 60,
    "minutes": 60,
    "min": 60,
    "m": 60,
    "hour": 3600,
    "hours": 3600,
    "h": 3600,
    "day": 86400,
    "days": 86400,
    "d": 86400,
}

def parse_rate(rate: str) -> Rate:
    """
    Parse strings like: "10/minute", "5/second", "100/hour".
    Returns (limit, period_seconds).
    """
    if not isinstance(rate, str):
        raise TypeError(f"rate must be str, got {type(rate)}")

    s = rate.strip()
    if "/" not in s:
        raise ValueError(f"Invalid rate format {rate!r}. Expected like '10/minute'.")

    left, right = s.split("/", 1)
    left = left.strip()
    right = right.strip().lower()

    try:
        limit = int(left)
    except ValueError as e:
        raise ValueError(f"Invalid rate limit in {rate!r}. Must be an integer.") from e

    if limit <= 0:
        raise ValueError(f"Rate limit must be > 0, got {limit} in {rate!r}.")

    if right not in _UNIT_SECONDS:
        raise ValueError(
            f"Unsupported rate unit {right!r} in {rate!r}. "
            f"Supported: {sorted(set(_UNIT_SECONDS.keys()))}"
        )

    period_seconds = _UNIT_SECONDS[right]
    return Rate(limit=limit, period_seconds=period_seconds)