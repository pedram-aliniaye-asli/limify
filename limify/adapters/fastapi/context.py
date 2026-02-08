# method	policy matcher
# path	endpoint rules
# route_pattern	policy engine
# headers	key / plan resolver
# auth_hints	key / plan resolver
# timestamp	algorithms
# client_ip


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



def build_request_context(request):
    # client IP extraction, fallback to headers for proxied setups
    if "x-forwarded-for" in request.headers:
        client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
    elif hasattr(request.client, "host"):
        client_ip = request.client.host
    else:
        client_ip = "unknown"

    # extract user info if available, optional
    user_id = getattr(request.state, "user_id", None)
    org_id = getattr(request.state, "org_id", None)
    api_key = request.headers.get("x-api-key")

    return RequestContext(
        method=request.method,
        path=request.url.path,
        client_ip=client_ip,
        user_id=user_id,
        org_id=org_id,
        api_key=api_key,
    )