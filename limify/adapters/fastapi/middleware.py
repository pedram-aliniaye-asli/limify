
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from limify.adapters.fastapi.context import build_request_context


class LimifyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limiter):
        super().__init__(app)
        self.limiter = limiter

    async def dispatch(self, request: Request, call_next):
        context = build_request_context(request)

        result = await self.limiter.check(context)

        if not result.allowed:
            response = JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
            )

            response.headers["Retry-After"] = str(result.reset_after)
            response.headers["X-RateLimit-Limit"] = str(result.limit)
            response.headers["X-RateLimit-Remaining"] = str(result.remaining)

            return response

        response = await call_next(request)

        response.headers["X-RateLimit-Limit"] = str(result.limit)
        response.headers["X-RateLimit-Remaining"] = str(result.remaining)

        return response
