import pytest
from types import SimpleNamespace
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Scope

from limify.adapters.fastapi.middleware import LimifyMiddleware


class MockLimiter:
    def __init__(self, result):
        self.result = result

    async def check(self, context):
        return self.result


def build_starlette_request(method="GET", path="/", headers=None):
    scope: Scope = {
        "type": "http",
        "method": method,
        "path": path,
        "headers": [
            (k.lower().encode(), v.encode())
            for k, v in (headers or {}).items()
        ],
        "client": ("127.0.0.1", 1234),
    }
    return Request(scope)

#Allowed request
@pytest.mark.asyncio
async def test_middleware_allows_request():
    limiter_result = SimpleNamespace(
        allowed=True,
        remaining=4,
        limit=5,
        reset_after=60,
    )

    middleware = LimifyMiddleware(
        app=None,
        limiter=MockLimiter(limiter_result),
    )

    request = build_starlette_request(path="/items")

    async def call_next(req):
        return Response("OK")

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 200
    assert response.headers["X-RateLimit-Limit"] == "5"
    assert response.headers["X-RateLimit-Remaining"] == "4"


#Blocked request
@pytest.mark.asyncio
async def test_middleware_blocks_request():
    limiter_result = SimpleNamespace(
        allowed=False,
        remaining=0,
        limit=5,
        reset_after=30,
    )

    middleware = LimifyMiddleware(
        app=None,
        limiter=MockLimiter(limiter_result),
    )

    request = build_starlette_request(path="/items")

    async def call_next(req):
        return Response("OK")  # Should NOT be called

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "30"
    assert response.headers["X-RateLimit-Limit"] == "5"
    assert response.headers["X-RateLimit-Remaining"] == "0"
    import json
    assert json.loads(response.body) == {"detail": "Rate limit exceeded"}

#Ensure call_next is not executed when blocked
@pytest.mark.asyncio
async def test_call_next_not_called_when_blocked():
    limiter_result = SimpleNamespace(
        allowed=False,
        remaining=0,
        limit=5,
        reset_after=30,
    )

    middleware = LimifyMiddleware(
        app=None,
        limiter=MockLimiter(limiter_result),
    )

    request = build_starlette_request(path="/items")

    called = False

    async def call_next(req):
        nonlocal called
        called = True
        return Response("OK")

    await middleware.dispatch(request, call_next)

    assert called is False