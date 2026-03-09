# Configuration

Limify uses `LimifyConfig` to define rules.

Example:

```python
config = LimifyConfig(
    rules=[
        {
            "id": "items",
            "method": "*",
            "path": "/items",
            "rate": "10/minute",
            "priority": 10,
        }
    ]
)
```

Higher priority rules override lower priority rules.
