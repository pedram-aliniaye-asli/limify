from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class LimifyConfig:
    rules: List[Dict[str, Any]]
    redis_url: str = "redis://localhost:6379"
    default_rule: Dict[str, Any] | None = None
