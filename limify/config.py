from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class LimifyConfig:
    rules: List[Dict[str, Any]]
    default_rule: Dict[str, Any] | None = None
