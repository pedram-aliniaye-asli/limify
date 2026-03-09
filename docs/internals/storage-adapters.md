# Storage Adapters

Storage adapters provide the persistence layer used by rate-limiting algorithms.

They are responsible for storing and retrieving the **token bucket state**.

Currently supported adapters:

- `RedisAsyncAdapter`
- `RedisSyncAdapter`

Both adapters interact with Redis but expose a simplified interface to the algorithm layer.

---

## Why Storage Adapters Exist

Limify separates **rate-limiting logic** from **data storage**.

This design follows the principles of clean architecture.

The algorithm should not need to know:

- which database is used
- how commands are executed
- whether the client is synchronous or asynchronous

Instead, the algorithm communicates with a storage adapter that abstracts these details.

This allows Limify to:

- support multiple storage backends
- support both sync and async execution
- remain framework independent
- simplify testing

---

## Redis-Based Storage

Limify currently uses Redis as the storage backend.

Redis is well suited for rate limiting because it provides:

- extremely low latency
- atomic operations
- Lua scripting support
- distributed access across multiple application instances

Each identity's rate limit state is stored in a Redis key.

Example key:

```
limify:items:default:user:42
```

Value stored in Redis:

```
tokens:last_timestamp
```

Example:

```
7:1718654321
```

Meaning:

```
tokens = 7
last_refill_timestamp = 1718654321
```

---

## RedisAsyncAdapter

`RedisAsyncAdapter` is designed for asynchronous Python applications.

It works with the `redis.asyncio` client.

Typical environments:

- FastAPI
- Starlette
- async workers
- asyncio-based services

Example usage:

```python
import redis.asyncio as redis
from limify.core.redis_adapter import RedisAsyncAdapter

redis_client = redis.from_url("redis://localhost:6379")

adapter = RedisAsyncAdapter(redis_client)
```

The async adapter exposes coroutine-based operations used by the algorithm.

Example operations:

```
script_load
evalsha
```

These methods allow the algorithm to execute Lua scripts asynchronously.

---

## RedisSyncAdapter

`RedisSyncAdapter` is designed for synchronous Python applications.

It works with the standard Redis client.

Typical environments:

- Flask
- Django
- background workers
- CLI applications

Example usage:

```python
import redis
from limify.core.redis_adapter import RedisSyncAdapter

redis_client = redis.Redis(host="localhost", port=6379)

adapter = RedisSyncAdapter(redis_client)
```

The synchronous adapter exposes the same interface but executes Redis commands synchronously.

---

## Adapter Responsibilities

Storage adapters are responsible for:

### Lua script loading

The token bucket algorithm loads its Lua script into Redis:

```
SCRIPT LOAD
```

This returns a script SHA identifier used for future execution.

---

### Script execution

Adapters execute the script using:

```
EVALSHA
```

Arguments passed to the script include:

```
limit
period_seconds
timestamp
```

The script performs all rate limit calculations atomically.

---

### Redis interaction abstraction

Instead of the algorithm calling Redis directly, it calls adapter methods such as:

```
script_load(...)
evalsha(...)
```

This abstraction makes the algorithm independent of the Redis client implementation.

---

## Why Not Call Redis Directly?

Without adapters, the algorithm would need to know:

- Redis client type
- async vs sync execution
- command syntax
- connection handling

Adapters isolate this complexity.

This improves:

- maintainability
- testability
- extensibility

---

## Example Flow

1. Limify receives a request
2. The limiter resolves the rule, plan, and identity
3. The algorithm calls the storage adapter
4. The adapter executes the Lua script in Redis
5. Redis updates the token bucket state
6. The algorithm returns the rate-limit decision

---

## Future Storage Adapters

The adapter architecture allows new storage backends to be implemented easily.

Potential future adapters:

```
InMemoryAdapter
PostgreSQLAdapter
MemcachedAdapter
Distributed cache systems
```

As long as the adapter implements the expected interface, it can be used by Limify algorithms.

---

## Summary

Storage adapters provide the persistence layer for Limify.

They:

- store rate limit state
- execute Redis Lua scripts
- abstract Redis client details
- support both sync and async execution

Currently supported adapters:

```
RedisAsyncAdapter
RedisSyncAdapter
```

This design keeps the algorithm layer clean and allows Limify to support multiple storage systems in the future.