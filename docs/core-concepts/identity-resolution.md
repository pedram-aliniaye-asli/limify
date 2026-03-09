# Identity Resolution

Identity resolution determines **who the rate limit applies to**.

Instead of limiting requests globally, Limify isolates rate limits per identity.

This ensures that one user or client cannot consume the entire rate limit for everyone else.

---

## Identity Priority

When a request arrives, Limify determines the request identity using the following priority order:

1. `user_id`
2. `org_id`
3. `api_key`
4. `client_ip`
5. `anonymous`

The **first available identity is used**.

Example request context:

```python
RequestContext(
    method="GET",
    path="/items",
    user_id=42,
    org_id=10,
    api_key=None,
    client_ip="127.0.0.1"
)
```

In this case:

```
user_id = 42
```

So the identity used will be:

```
user:42
```

Even though `org_id` and `client_ip` exist, they are ignored because `user_id` has higher priority.

---

## Why Identity Priority Exists

Different applications identify clients differently.

For example:

| Scenario | Best Identity |
|------|------|
Authenticated user | `user_id`
Multi-tenant SaaS | `org_id`
Public API | `api_key`
Anonymous traffic | `client_ip`

The priority system allows Limify to automatically choose the **most specific identity available**.

---

## Redis Key Structure

Once an identity is selected, Limify constructs a deterministic Redis key.

Format:

```
limify:{rule_id}:{plan_id}:{identity_type}:{identity_value}
```

Example keys:

```
limify:items:default:user:42
limify:items:pro:apikey:abc123
limify:default:default:ip:127.0.0.1
```

This ensures that each identity has a **separate token bucket**.

---

## Independent Rate Limit Buckets

Each identity receives its own rate limit bucket.

Example rule:

```
10/minute
```

Requests:

```
User 1 → 10/minute
User 2 → 10/minute
User 3 → 10/minute
```

User 1 exhausting their quota does **not affect other users**.

---

## Example Scenario

Rule:

```
10/minute
```

Requests:

```
User A → 10 requests allowed
User B → 10 requests allowed
User C → 10 requests allowed
```

Each user has their own bucket:

```
limify:items:default:user:A
limify:items:default:user:B
limify:items:default:user:C
```

---

## Anonymous Traffic

If no identity is provided in the request context, Limify falls back to the client IP.

Example:

```
client_ip = 192.168.1.10
```

Redis key:

```
limify:default:default:ip:192.168.1.10
```

This allows Limify to rate limit anonymous clients.

---

## RequestContext

Identity resolution uses the `RequestContext` object.

Example:

```python
RequestContext(
    method="GET",
    path="/items",
    user_id=42,
    org_id=None,
    api_key=None,
    client_ip="127.0.0.1"
)
```

Framework adapters (like FastAPI middleware) are responsible for constructing this context.

---

## Why This Design Matters

This design enables:

### Multi-tenant SaaS platforms

Organizations receive independent rate limits.

### User-based rate limiting

Authenticated users are isolated from each other.

### Public APIs

API keys can be rate limited independently.

### Anonymous traffic control

IP-based limits protect services from abuse.

---

## Summary

Identity resolution determines **who the rate limit applies to**.

Limify selects the identity using the following priority:

```
user_id → org_id → api_key → client_ip → anonymous
```

Each identity produces its own Redis key and receives an independent rate limit bucket.