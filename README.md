<h1 align="center">Limify</h1>

<p align="center">
Framework-agnostic, Redis-backed rate limiting engine for modern Python systems.
</p>

<p align="center">
  <img src="https://img.shields.io/pypi/v/limifyrate" alt="PyPI">
  <img src="https://img.shields.io/pypi/pyversions/limifyrate" alt="Python versions">
  <img src="https://img.shields.io/github/license/pedram-aliniaye-asli/limify" alt="License">
  <a href="https://pedram-aliniaye-asli.github.io/limify">
    <img src="https://img.shields.io/badge/docs-mkdocs-blue" alt="Docs">
  </a>
</p>



Limify provides a clean-architecture rate limiting core with pluggable storage adapters, async and sync support, atomic Redis Lua execution, and framework adapters.

Limify is designed as infrastructure-level software for backend engineers, microservices, and API platforms.

---
## Documentation

https://pedram-aliniaye-asli.github.io/limify

---
## Features

* Framework-agnostic core
* Async and sync Redis support
* Atomic Redis Lua token bucket implementation
* FastAPI / Starlette middleware adapter
* Rule-based rate limiting with wildcard matching
* Plan-based rate limiting support
* Multi-identity support:

  * user_id
  * org_id
  * api_key
  * client_ip
* Clean architecture with dependency injection
* Pluggable storage and algorithms
* Fully testable design

---

## Architecture

Limify uses layered clean architecture:

```
Application (FastAPI / Flask / etc.)
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

Core is fully independent of frameworks.

---

## Installation

### Core only

```
pip install limifyrate
```

### With FastAPI / Starlette adapter

```
pip install "limifyrate[fastapi]"
```

### Development install

```
git clone https://github.com/pedram-aliniaye-asli/limify.git
cd limify
pip install -e ".[dev]"
```

---

## Requirements

* Python 3.10+
* Redis

---

## Quick Start (Async)

Example using async Redis and FastAPI.

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
            "path": "/**", # Matches all endpoints (demo only) — not recommended.
            "rate": "5/minute",
            "priority": 0,
        },
        {
            "id": "items",
            "method": "*",
            "path": "/items",
            "rate": "10/minute",
            "priority": 10,
        },
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

---

## Sync Example

Example using synchronous Redis.

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

---

## Redis Key Structure

Limify generates deterministic keys:

```
limify:{rule_id}:{plan_id}:{identity_type}:{identity_value}
```

Examples:

```
limify:items:default:user:42
limify:default:default:ip:127.0.0.1
limify:items:pro:apikey:abc123
```

Each identity and rule has an independent token bucket.

---

## Rules

Rules define rate limits per endpoint.

Example:

```python
{
    "id": "items",
    "method": "*",
    "path": "/items",
    "rate": "10/minute",
    "priority": 10,
}
```

Supported wildcards:

```
/items/*
/api/**
```

Higher priority rules override lower priority ones.

---

## Identity Resolution Priority

Default resolution order:

1. user_id
2. org_id
3. api_key
4. client_ip
5. anonymous

---

## Plan Support

Limify supports plan-based rate limiting using PlanProvider.

This enables multi-tier SaaS limits.

Example plans:

```
free → 10/minute
pro → 100/minute
enterprise → 1000/minute
```

---

## Algorithms

Currently implemented:

* Token Bucket (async)
* Token Bucket (sync)

Future:

* Sliding Window
* Fixed Window

---

## Storage Adapters

Currently implemented:

* RedisAsyncAdapter
* RedisSyncAdapter

Future:

* In-memory adapter
* PostgreSQL adapter

---

## FastAPI Adapter

Limify provides Starlette-compatible middleware.

```
limify.adapters.fastapi.middleware.LimifyMiddleware
```

Adds headers:

```
X-RateLimit-Limit
X-RateLimit-Remaining
Retry-After
```

---

## Project Structure

```
limify/
  adapters/
    fastapi/
  core/
    algorithms/
    resolvers/
    redis_adapter.py
    limiter.py
    ...
  config.py
  defaults.py
  plan_provider.py
  ...
```

---

## Status

Alpha

Core architecture is stable and production-grade, but API surface may evolve.

---

## Roadmap

* In-memory storage adapter
* Flask adapter
* Django adapter
* Sliding window algorithm
* Fixed window algorithm
* Metrics support

---

## License

MIT License

---

## Author

Pedram Aliniaye Asli

---

Limify is designed as reusable infrastructure for modern backend systems.
