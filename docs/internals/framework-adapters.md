# Framework Adapters

Framework adapters integrate Limify with web frameworks.

They connect the **framework request lifecycle** with Limify’s **rate-limiting engine**.

Currently supported adapters:

- FastAPI
- Starlette

These adapters are implemented as **middleware**.

---

## What Framework Adapters Do

Framework adapters are responsible for:

1. Intercepting incoming requests
2. Extracting request metadata
3. Constructing a `RequestContext`
4. Calling the Limify limiter
5. Blocking requests when limits are exceeded
6. Adding rate limit headers to responses

The adapter layer allows Limify to remain **framework-agnostic**.

The core Limify engine does not depend on any specific web framework.

---

## Middleware Integration

Framework adapters are implemented as middleware components.

Middleware sits between the HTTP server and your application endpoints.

Request flow:

```
Client Request
      ↓
Framework Middleware (Limify)
      ↓
Limiter
      ↓
Application Endpoint
```

If a request exceeds its rate limit, the middleware immediately returns an error response.

---

## FastAPI Adapter

Limify provides a FastAPI-compatible middleware:

```
limify.adapters.fastapi.middleware.LimifyMiddleware
```

Example usage:

```python
from fastapi import FastAPI
from limify.adapters.fastapi.middleware import LimifyMiddleware

app = FastAPI()

app.add_middleware(
    LimifyMiddleware,
    limiter=limify.limiter,
)
```

Once installed, all requests passing through the application will be evaluated by Limify.

---

## Starlette Compatibility

FastAPI is built on top of **Starlette**, so the middleware is compatible with both frameworks.

This means Limify can work with:

- FastAPI
- Starlette
- other ASGI frameworks that support Starlette-style middleware

---

## RequestContext Construction

When a request arrives, the middleware constructs a `RequestContext` object.

Example:

```python
RequestContext(
    method="GET",
    path="/items",
    user_id=None,
    org_id=None,
    api_key=None,
    client_ip="127.0.0.1"
)
```

The context contains the information needed for:

- rule matching
- identity resolution
- plan resolution

Framework adapters are responsible for extracting this information from the request.

---

## Rate Limit Enforcement

The middleware sends the request context to the Limify limiter:

```
limiter.check(context)
```

The limiter then:

1. resolves the matching rule
2. resolves the applicable plan
3. resolves the request identity
4. executes the rate-limiting algorithm

If the request is allowed, the middleware forwards it to the application endpoint.

If the request exceeds its limit, the middleware immediately returns an error response.

---

## Rate Limit Headers

Limify adds standard rate limit headers to responses.

These headers help clients understand their current rate limit status.

### X-RateLimit-Limit

The maximum number of requests allowed in the current period.

Example:

```
X-RateLimit-Limit: 100
```

---

### X-RateLimit-Remaining

The number of requests remaining before the rate limit is reached.

Example:

```
X-RateLimit-Remaining: 42
```

---

### Retry-After

Indicates how long the client should wait before making another request.

Example:

```
Retry-After: 12
```

This value is returned when the rate limit has been exceeded.

---

## Rate Limit Response

If a request exceeds its rate limit, the middleware returns an HTTP error.

Typical response:

```
HTTP/1.1 429 Too Many Requests
```

Example response body:

```json
{
  "detail": "Rate limit exceeded"
}
```

The `Retry-After` header indicates when requests can resume.

---

## Example Flow

A request arrives:

```
GET /items
```

Middleware steps:

1. Build `RequestContext`
2. Call limiter
3. Execute token bucket algorithm
4. Receive result

If allowed:

```
→ Request proceeds to endpoint
```

If blocked:

```
→ HTTP 429 returned
```

---

## Why Framework Adapters Matter

Framework adapters allow Limify to support multiple environments without modifying core logic.

Benefits:

### Framework independence

Core rate-limiting logic remains separate from framework code.

### Easy integration

Middleware installation requires only a few lines of code.

### Consistent behavior

All supported frameworks use the same rate-limiting engine.

---

## Future Framework Adapters

Future versions of Limify may include adapters for additional frameworks:

```
Flask
Django
ASGI middleware (generic)
API gateway integrations
```

Because Limify separates adapters from core logic, adding new frameworks is straightforward.

---

## Summary

Framework adapters connect Limify with web frameworks.

They:

- intercept requests
- construct request contexts
- call the rate limiter
- enforce limits
- add rate limit headers

Currently supported adapters:

```
FastAPI
Starlette
```

These adapters allow Limify to integrate seamlessly into modern Python web applications.