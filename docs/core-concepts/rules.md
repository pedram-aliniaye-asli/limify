# Rules

Rules define rate limits for endpoints.

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
