# Limify

Limify is a Redis-backed, framework-agnostic rate limiting engine for Python.

It provides a clean architecture core with pluggable adapters, async and sync execution, and atomic Redis Lua algorithms.

Limify is designed for:

- Backend engineers
- API platforms
- Microservices architectures
- SaaS platforms with multi-tier limits

---

## Key Features

- Framework-agnostic core
- Async and sync Redis support
- Atomic Redis Lua execution
- Rule-based rate limiting
- Plan-based rate limiting
- Multiple identity types
- Clean architecture design
- Pluggable algorithms and storage

---

## Example

```python
from limify import Limify, LimifyConfig

config = LimifyConfig(
    rules=[
        {
            "id": "items",
            "method": "*",
            "path": "/items",
            "rate": "10/minute",
        }
    ]
)
```

Use the navigation menu to explore the documentation.
