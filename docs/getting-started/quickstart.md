# Quick Start

This guide shows how to integrate **Limify** into a Python application.

Limify supports both **async** and **sync** Redis clients.

---

## Install

Core package:

```
pip install limifyrate
```

With FastAPI adapter:

```
pip install "limifyrate[fastapi]"
```

---

## Async Example (FastAPI)

```python
import redis.asyncio as redis

from fastapi import FastAPI
from limify import Limify, LimifyConfig
from limify.adapters.fastapi.middleware import LimifyMiddleware
from limify.core.redis_adapter import RedisAsyncAdapter
from limify.core.algorithms.token_bucket import AsyncTokenBucketAlgorithm


redis_client = redis.from_url("redis://localhost:6379")

adapter = RedisAsyncAdapter(redis_client)

algorithm = AsyncTokenBucketAlgorithm(adapter)
await algorithm.initialize()

config = LimifyConfig(
    rules=[
        {
            "id": "default",
            "method": "*",
            "path": "/**",
            "rate": "5/minute",
        }
    ]
)

limify = Limify(
    algorithm=algorithm,
    config=config,
)

app = FastAPI()

app.add_middleware(
    LimifyMiddleware,
    limiter=limify.limiter,
)


@app.get("/items")
async def items():
    return {"status": "ok"}
```

Requests exceeding the configured rate will return **HTTP 429**.

---

## Sync Example

```python
import redis

from limify import Limify, LimifyConfig
from limify.core.redis_adapter import RedisSyncAdapter
from limify.core.algorithms.token_bucket import TokenBucketAlgorithm


redis_client = redis.Redis(host="localhost", port=6379)

adapter = RedisSyncAdapter(redis_client)

algorithm = TokenBucketAlgorithm(adapter)

config = LimifyConfig(
    rules=[
        {
            "id": "default",
            "method": "*",
            "path": "/**",
            "rate": "5/minute",
        }
    ]
)

limify = Limify(
    algorithm=algorithm,
    config=config,
)
```

The sync version can be used in synchronous frameworks or background workers.

---

## What Happens Internally

For each request Limify:

1. Resolves the matching rule
2. Determines the active plan
3. Builds an identity key
4. Executes the rate-limiting algorithm
5. Allows or blocks the request

The token bucket state is stored in **Redis** and updated atomically using **Lua scripts**.