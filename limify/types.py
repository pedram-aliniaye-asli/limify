from dataclasses import dataclass


@dataclass
class LimitationResult:
    allowed: bool
    remaining: int
    limit: int
    reset_after: int
