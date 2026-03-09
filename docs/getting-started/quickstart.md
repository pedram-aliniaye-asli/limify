# Quick Start

Example using FastAPI with async Redis.

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
```
