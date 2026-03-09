# Algorithms

Limify enforces rate limits using **rate-limiting algorithms**.

Algorithms are responsible for deciding whether a request should be:

- allowed
- delayed
- rejected

They operate on numeric parameters derived from rules and plans.

Currently implemented:

- **Token Bucket (sync)**
- **Token Bucket (async)**

Both implementations share the same logic but use different Redis clients.

---

## Token Bucket

The **Token Bucket algorithm** is a widely used rate-limiting technique that allows bursts while maintaining a controlled average request rate.

Instead of simply counting requests per window, it models rate limiting as a **bucket filled with tokens**.

Requests consume tokens from the bucket.

If the bucket becomes empty, requests are rejected.

---

## Concept

Each identity has a **bucket** containing tokens.

The bucket has three parameters:

```
capacity       → maximum tokens in the bucket
refill rate    → tokens added per second
current tokens → tokens available now
```

Example configuration:

```
10/minute
```

Converted internally:

```
limit = 10
period_seconds = 60
refill_rate = 10 / 60 = 0.1667 tokens per second
```

This means the bucket:

- can hold **10 tokens**
- refills **0.1667 tokens every second**

---

## Request Flow

When a request arrives, Limify performs the following steps.

### 1. Load bucket state

The current bucket state is retrieved from Redis.

Stored format:

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

### 2. Refill tokens

Limify calculates how many tokens should have been refilled since the last request.

Formula:

```
refill = (now - last_timestamp) * refill_rate
```

Example:

```
last_timestamp = 100
now = 110
refill_rate = 0.1667

refill = (110 - 100) * 0.1667 = 1.667 tokens
```

The bucket is updated:

```
tokens = min(capacity, tokens + refill)
```

The bucket never exceeds its maximum capacity.

---

### 3. Consume a token

If the bucket contains at least one token:

```
tokens >= 1
```

The request is allowed and one token is consumed.

```
tokens = tokens - 1
```

---

### 4. Reject request

If the bucket is empty:

```
tokens < 1
```

The request is rejected.

In web frameworks, this results in:

```
HTTP 429 Too Many Requests
```

---

## Burst Handling

Token Bucket allows short bursts of traffic.

Example:

Rule:

```
10/minute
```

Bucket capacity:

```
10 tokens
```

A client may immediately send:

```
10 requests at once
```

But after that, the client must wait for tokens to refill.

Refill speed:

```
1 token every 6 seconds
```

This behavior makes Token Bucket ideal for APIs.

---

## Redis Storage

Each identity has a separate bucket stored in Redis.

Example key:

```
limify:items:default:user:42
```

Value format:

```
tokens:last_timestamp
```

Example:

```
4:1718654400
```

This means:

```
tokens = 4
last_refill_timestamp = 1718654400
```

---

## Redis Lua Execution

Limify executes the token bucket logic using **Redis Lua scripts**.

Example operations performed in the script:

```
1. read current bucket state
2. calculate token refill
3. update token count
4. store new state
5. return remaining tokens
```

The script receives arguments:

```
ARGV[1] → limit
ARGV[2] → period_seconds
ARGV[3] → current timestamp
```

From these values it computes:

```
refill_rate = limit / period_seconds
```

---

## Why Lua Is Used

Lua scripts allow the entire rate-limiting process to run **inside Redis**.

Benefits:

### Atomic execution

All calculations and updates happen in a single Redis operation.

This prevents race conditions when multiple servers process requests simultaneously.

### Distributed safety

Multiple API servers can share the same Redis instance without corrupting bucket state.

### High performance

Instead of multiple Redis commands:

```
GET
CALCULATE
SET
```

Lua executes everything in one atomic operation.

---

## Sync vs Async Algorithms

Limify provides two implementations.

### AsyncTokenBucketAlgorithm

Uses `redis.asyncio` and is intended for asynchronous frameworks such as:

- FastAPI
- Starlette
- async workers

Example initialization:

```python
algorithm = AsyncTokenBucketAlgorithm(redis_adapter)
await algorithm.initialize()
```

---

### TokenBucketAlgorithm

Uses the synchronous Redis client and works with synchronous applications.

Example:

```python
algorithm = TokenBucketAlgorithm(redis_adapter)
```

Both versions use the same Lua script and enforce identical behavior.

---

## Why Token Bucket Was Chosen

Token Bucket provides several advantages:

### Burst tolerance

Allows short bursts of requests.

### Smooth refill behavior

Limits traffic without harsh fixed windows.

### Efficient implementation

Requires minimal storage and simple calculations.

### Widely adopted

Used by systems such as:

- NGINX
- Envoy
- API gateways
- cloud rate limiters

---

## Future Algorithms

Future versions of Limify may include additional algorithms such as:

```
Sliding Window
Fixed Window
Leaky Bucket
```

These algorithms serve different traffic patterns and system requirements.

---

## Summary

Limify currently uses the **Token Bucket algorithm** to enforce rate limits.

The algorithm:

1. refills tokens over time
2. consumes tokens per request
3. rejects requests when tokens are empty

Bucket state is stored in Redis and updated using **atomic Lua scripts**, ensuring safe operation in distributed systems.