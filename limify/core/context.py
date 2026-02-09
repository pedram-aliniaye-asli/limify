from dataclasses import dataclass, field 
from datetime import datetime, timezone

@dataclass(frozen=True)
class RequestContext:
    method: str
    path: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    client_ip: str|None = None
    user_id: str|None = None
    org_id: str|None = None
    api_key: str|None = None
