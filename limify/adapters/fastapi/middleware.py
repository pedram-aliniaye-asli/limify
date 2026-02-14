
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from datetime import datetime, timezone
from limify.adapters.fastapi.context import build_request_context

current_utc_timestamp = datetime.now(timezone.utc).timestamp()
print(current_utc_timestamp)

class LimifyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Logic to execute BEFORE the request is processed
        request_context = build_request_context(request)
        print(f"request will be sent for parsing for data like endpoint and method and the rest of the way")
        print(request_context)
        # Forward the request to the next middleware/route handler
        response = await call_next(request)
        return response


# TO-DO: adding the custom headers here
# TO-DO: adding the wirings