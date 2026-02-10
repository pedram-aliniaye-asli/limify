from dataclasses import dataclass

@dataclass(frozen=True)
class Plan:
    id: str
    limit: int
    period_seconds: int
