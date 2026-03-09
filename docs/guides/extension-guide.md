# Extension Guide

Limify is designed to be extensible.

Its architecture separates:

- framework integration
- request resolution
- rate-limiting logic
- storage persistence

This makes it possible to extend Limify without modifying the core behavior.

Typical extension points include:

- custom algorithms
- custom storage adapters
- custom plan providers
- custom framework adapters

This guide focuses on the two main extension points:

- **custom algorithms**
- **custom storage adapters**

---

## Extension Philosophy

Limify follows a clean architecture approach.

The core idea is:

- algorithms should not depend on frameworks
- storage should not depend on business logic
- adapters should isolate external systems

This means each extension should have a **single responsibility**.

For example:

- an algorithm decides whether a request is allowed
- a storage adapter persists and retrieves state
- a framework adapter translates HTTP requests into Limify context objects

Keeping those boundaries clear makes extensions easier to test and maintain.

---

## Custom Algorithm

A custom algorithm is useful when Token Bucket is not the best fit for your traffic model.

Examples of alternative algorithms:

- Sliding Window
- Fixed Window
- Leaky Bucket
- concurrency limits
- quota-based limits

A custom algorithm should implement the same role as the built-in algorithms:

1. receive the resolved key and plan
2. retrieve/update state through the storage adapter
3. return the rate-limit decision

---

## What an Algorithm Needs

A Limify algorithm typically works with:

- a **key** that uniquely identifies the rate limit bucket
- a **plan** containing:
  - `id`
  - `limit`
  - `period_seconds`
- a **storage adapter**
- the current timestamp

The algorithm should return a result that indicates:

- whether the request is allowed
- how many requests remain
- how long until reset or retry

This keeps the algorithm independent of frameworks and request objects.

---

## Responsibilities of an Algorithm

A custom algorithm should be responsible for:

- interpreting the rate limit values
- reading current state
- updating state
- deciding allow/block
- returning structured output

A custom algorithm should **not** be responsible for:

- HTTP responses
- request parsing
- identity selection
- plan lookup
- framework-specific behavior

Those responsibilities belong to other layers.

---

## Example: Custom Fixed Window Algorithm

Below is a simplified conceptual example:

```python
import time
from dataclasses import dataclass


@dataclass
class LimitationResult:
    allowed: bool
    remaining: int
    reset_after: int


class FixedWindowAlgorithm:
    def __init__(self, storage):
        self.storage = storage

    def check(self, key, plan):
        now = int(time.time())
        window_start = now - (now % plan.period_seconds)
        window_key = f"{key}:{window_start}"

        current = self.storage.get(window_key) or 0

        if current >= plan.limit:
            reset_after = plan.period_seconds - (now % plan.period_seconds)
            return LimitationResult(
                allowed=False,
                remaining=0,
                reset_after=reset_after,
            )

        self.storage.increment(window_key, ttl=plan.period_seconds)

        return LimitationResult(
            allowed=True,
            remaining=max(plan.limit - current - 1, 0),
            reset_after=plan.period_seconds - (now % plan.period_seconds),
        )
```

This example is intentionally simplified, but it shows the core idea:

- calculate the active window
- count requests in that window
- reject if the limit is reached
- otherwise increment the count

---

## Async Custom Algorithm

For async applications, your algorithm may need async methods.

Example shape:

```python
class AsyncCustomAlgorithm:
    def __init__(self, storage):
        self.storage = storage

    async def check(self, key, plan):
        ...
```

This is similar to Limify’s `AsyncTokenBucketAlgorithm`.

---

## Using the Storage Adapter

Algorithms should rely on the storage adapter instead of talking directly to Redis or another backend.

Why:

- easier to test
- easier to replace storage backends
- cleaner architecture
- consistent interface

For example, the built-in token bucket algorithm uses the storage adapter to:

- load a Lua script
- execute it atomically
- retrieve the updated bucket state

Your custom algorithm should follow the same principle.

---

## Testing a Custom Algorithm

A custom algorithm should be tested independently from framework code.

Typical tests should verify:

- request allowed when under limit
- request blocked when limit exceeded
- state updates correctly
- retry/reset values are correct
- storage failures are handled properly

Because the algorithm is isolated, it should be possible to test it using:

- mocked storage adapters
- fake storage backends
- deterministic timestamps

---

## Custom Storage

A custom storage adapter allows Limify to persist rate-limit state in a backend other than Redis.

Examples of possible storage backends:

- in-memory storage
- PostgreSQL
- Memcached
- distributed cache services
- custom internal infrastructure

Storage adapters are responsible for providing the persistence operations needed by algorithms.

---

## Why Storage Is Abstracted

Limify algorithms should not depend on:

- Redis client details
- connection handling
- sync vs async command syntax
- backend-specific APIs

Instead, they depend on an abstraction.

This allows the same algorithm design to work across different storage systems.

---

## Current Built-In Storage Adapters

Limify currently includes:

- `RedisSyncAdapter`
- `RedisAsyncAdapter`

These adapters provide the persistence and script execution functionality required by the built-in token bucket algorithm.

---

## Responsibilities of a Storage Adapter

A storage adapter should be responsible for:

- communicating with the backend
- reading and writing state
- exposing a clean interface to algorithms
- hiding backend-specific implementation details

A storage adapter should **not** contain rate-limiting policy logic.

That logic belongs in the algorithm.

---

## Minimal Redis-Compatible Interface

Your current token bucket algorithm expects Redis-oriented behavior, including:

- `script_load(...)`
- `evalsha(...)`

That is because the built-in token bucket implementation uses Lua for atomic execution.

So if you want to support the existing token bucket algorithm with another backend, you would need an adapter that can provide equivalent behavior.

---

## Example: In-Memory Storage Adapter

For simpler algorithms or testing, you can build an in-memory adapter.

Example:

```python
class InMemoryStorage:
    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value

    def increment(self, key, ttl=None):
        self.data[key] = self.data.get(key, 0) + 1
        return self.data[key]
```

This is useful for:

- testing
- local development
- prototypes

However, it is **not suitable for distributed production systems**, because each process would maintain separate state.

---

## Matching Storage to Algorithm

Not every storage adapter fits every algorithm.

Examples:

### Token Bucket with Redis Lua
Best suited for:

- Redis
- atomic scripting support
- distributed systems

### Fixed Window with In-Memory Storage
Best suited for:

- local development
- testing
- single-process applications

So when building a custom algorithm or adapter, think of them as a pair:

- algorithm design
- storage capability

---

## Designing a Clean Adapter Interface

If you plan to support multiple backends in the future, it may be useful to define a formal adapter protocol or base class.

For example:

```python
class StorageAdapter:
    def get(self, key):
        raise NotImplementedError

    def set(self, key, value):
        raise NotImplementedError

    def increment(self, key, ttl=None):
        raise NotImplementedError
```

Or for Redis-script-based algorithms:

```python
class ScriptStorageAdapter:
    def script_load(self, script: str):
        raise NotImplementedError

    def evalsha(self, sha: str, num_keys: int, *args):
        raise NotImplementedError
```

This makes extension more predictable and easier to document.

---

## Custom Framework Adapters

Although this page focuses on algorithms and storage, Limify can also be extended with new framework adapters.

A framework adapter should:

- intercept requests
- extract method/path/client metadata
- build a `RequestContext`
- call the limiter
- enforce the result in framework-specific form

This is how the FastAPI/Starlette middleware works.

Future adapters could target:

- Flask
- Django
- generic ASGI
- API gateway integrations

---

## Best Practices for Extensions

When extending Limify:

### Keep responsibilities narrow

Do not mix framework logic, algorithm logic, and storage code in the same component.

### Reuse existing abstractions

Use `RequestContext`, `Plan`, and Limify’s core flow instead of bypassing them.

### Prefer deterministic behavior

Rate limiting should behave consistently under concurrency and load.

### Test extensions independently

A custom algorithm or adapter should be testable in isolation.

### Document assumptions clearly

If your algorithm depends on atomic storage operations, note that explicitly.

---

## Summary

Limify is designed to be extended in a clean and predictable way.

You can extend it by adding:

- custom algorithms
- custom storage adapters
- custom plan providers
- custom framework adapters

A custom algorithm should focus on **rate-limiting logic**.

A custom storage adapter should focus on **persistence and backend communication**.

Keeping these responsibilities separate preserves Limify’s architecture and makes the system easier to evolve.