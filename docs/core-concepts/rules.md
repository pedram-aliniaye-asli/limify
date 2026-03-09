# Rules

Rules define how rate limits are applied to incoming requests.

Each rule specifies:

- which requests it applies to
- what rate limit should be enforced
- how rules are prioritized

Rules are configured through `LimifyConfig`.

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

---

## Rule Fields

### id

Unique identifier for the rule.

Example:

```
"id": "items"
```

The rule ID is used internally to construct rate-limit keys.

Example Redis key:

```
limify:items:default:user:42
```

Using stable rule IDs helps with monitoring and debugging.

---

### method

Defines which HTTP method the rule applies to.

Example:

```
"method": "GET"
```

Supported values:

- specific HTTP method (`GET`, `POST`, etc.)
- `"*"` for all methods

Example:

```
"method": "*"
```

This rule will apply to **all HTTP methods**.

---

### path

Defines the endpoint pattern the rule applies to.

Example:

```
"path": "/items"
```

Paths are matched against the request path using pattern matching.

---

## Wildcard Matching

Limify supports wildcard patterns to match multiple endpoints.

### Single segment wildcard

```
/items/*
```

Matches:

```
/items/1
/items/abc
/items/test
```

But does NOT match:

```
/items/1/edit
```

---

### Multi-segment wildcard

```
/api/**
```

Matches:

```
/api/users
/api/items/1
/api/v1/orders/123
```

The `**` wildcard matches **any remaining path segments**.

---

## Rule Priority

Rules may overlap.

To resolve conflicts, Limify uses **priority values**.

Higher priority rules take precedence.

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

Example conflict:

Rule A:

```
path = "/api/**"
priority = 0
```

Rule B:

```
path = "/api/users"
priority = 10
```

A request to:

```
/api/users
```

will match **Rule B**, because it has higher priority.

---

## Rule Evaluation

When a request arrives, Limify:

1. Collects all rules matching the request method and path
2. Sorts matching rules by priority
3. Selects the highest priority rule
4. Applies the associated rate limit

This ensures deterministic behavior even with overlapping rules.

---

## Example Rule Set

Example configuration:

```python
rules = [
    {
        "id": "default",
        "method": "*",
        "path": "/**",
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
```

Behavior:

```
GET /items        → 10/minute
GET /users        → 5/minute
POST /items       → 10/minute
```

The `items` rule overrides the default rule due to higher priority.

---

## Best Practices

### Use a default rule

Define a catch-all rule:

```
"path": "/**"
```

This ensures all endpoints have a rate limit.

---

### Use specific rules for critical endpoints

Example:

```
/login
/register
/payment
```

These endpoints often require stricter limits.

---

### Keep rule IDs stable

Changing rule IDs changes the Redis key structure, which resets rate-limit state.

---

## Summary

Rules control **how rate limits apply to requests**.

They define:

- request matching (method + path)
- rate limits
- rule priority

Combined with plans and identity resolution, rules form the foundation of Limify's rate-limiting behavior.