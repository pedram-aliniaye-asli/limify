from limify.core.context import RequestContext


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