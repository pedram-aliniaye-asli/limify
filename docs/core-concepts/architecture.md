# Architecture

Limify follows a layered **clean architecture** that separates framework code, rate-limiting logic, and storage concerns.

This allows Limify to remain **framework-agnostic**, highly testable, and easily extensible.

```
Application (FastAPI / etc.)  
        ↓  
Adapter (Middleware)  
        ↓  
Limiter (Orchestrator)  
        ↓  
Resolvers  
  ├─ RuleResolver  
  ├─ PlanResolver  
  └─ KeyResolver  
        ↓  
Algorithm (Token Bucket)  
        ↓  
Storage Adapter (Redis)  
```

Each layer has a specific responsibility and communicates only with the layer directly below it.

---

## Application Layer

The application layer represents the host framework.

Examples:

- FastAPI
- Starlette
- Flask
- background workers
- API gateways

Applications define **endpoints** and attach Limify middleware to enforce rate limits.

Limify does not depend on any framework directly.

---

## Adapter Layer (Middleware)

Adapters integrate Limify with web frameworks.

For example:

```
limify.adapters.fastapi.middleware.LimifyMiddleware
```

Responsibilities:

- Intercept incoming requests
- Extract request metadata
- Construct a `RequestContext`
- Call the Limiter
- Return HTTP 429 if the request is blocked
- Attach rate limit headers to responses

This layer translates **framework objects → Limify core objects**.

---

## Limiter (Orchestrator)

The `Limiter` is the central component that coordinates the rate-limiting process.

Responsibilities:

1. Resolve the matching rule
2. Resolve the active plan
3. Resolve the identity key
4. Execute the algorithm
5. Return the rate-limit result

The limiter itself contains **no framework logic and no storage logic**.

It only orchestrates the core components.

---

## Resolvers

Resolvers determine how requests map to rate limits.

They are responsible for interpreting request metadata.

### RuleResolver

Determines which rule applies to the request.

Rules are matched based on:

- HTTP method
- request path
- wildcard patterns
- priority order

Example rule:

```python
{
    "id": "items",
    "method": "*",
    "path": "/items",
    "rate": "10/minute",
    "priority": 10,
}
```

Rules with higher priority override lower priority ones.

---

### PlanResolver

Determines which **plan** applies to the request.

Plans allow Limify to support **multi-tier SaaS limits**.

Examples:

```
free → 10/minute
pro → 100/minute
enterprise → 1000/minute
```

The resolver may obtain plans from:

- a custom `PlanProvider`
- the rule's rate definition

If no custom plan exists, Limify derives a plan from the rule rate.

---

### KeyResolver

Determines the **identity key** used for rate limiting.

Limify supports multiple identity types.

Default resolution order:

1. `user_id`
2. `org_id`
3. `api_key`
4. `client_ip`
5. anonymous

The final Redis key format:

```
limify:{rule_id}:{plan_id}:{identity_type}:{identity_value}
```

Example:

```
limify:items:default:user:42
```

Each identity receives its own independent rate-limit bucket.

---

## Algorithm Layer

The algorithm implements the rate-limiting logic.

Currently implemented:

- Token Bucket (sync)
- Token Bucket (async)

The algorithm:

1. Reads the current token state
2. Refills tokens based on elapsed time
3. Consumes tokens for the request
4. Determines if the request is allowed

Algorithms operate purely on numeric values:

```
limit
period_seconds
```

They are independent of request context and framework code.

---

## Storage Adapter Layer

The storage adapter provides persistent state for algorithms.

Currently supported:

- `RedisAsyncAdapter`
- `RedisSyncAdapter`

Storage adapters handle:

- loading Lua scripts
- executing scripts
- interacting with Redis

---

## Redis Lua Execution

Limify executes rate-limit logic using Redis Lua scripts.

Benefits:

- atomic execution
- no race conditions
- safe in distributed systems
- consistent across multiple workers

The Lua script:

- calculates token refill
- updates bucket state
- returns remaining tokens

This guarantees correct behavior even under high concurrency.

---

## Why This Architecture Matters

This architecture enables:

### Framework independence

Limify can integrate with any Python framework.

### Testability

Core logic can be tested without Redis or frameworks.

### Extensibility

New algorithms or storage systems can be added easily.

### Maintainability

Each component has a single responsibility.

---

## Summary

The Limify architecture separates concerns into independent layers:

- adapters integrate frameworks
- resolvers determine rules and identities
- the limiter orchestrates execution
- algorithms enforce rate limits
- storage adapters persist state

This design makes Limify suitable for **high-performance distributed systems** and **modern backend platforms**.