# Rate Format

Limify expresses rate limits using a human-readable format:

```
<limit>/<unit>
```

Example:

```
10/minute
```

This means **10 requests are allowed per minute**.

Internally, Limify converts this format into numeric values used by the rate-limiting algorithm.

Example conversion:

```
10/minute → limit = 10, period_seconds = 60
```

---

## Syntax

A rate definition contains two parts:

```
limit / unit
```

### limit

The maximum number of requests allowed during the specified time unit.

Example:

```
5/minute
```

Limit = **5 requests**

---

### unit

Defines the time window for the rate limit.

Example:

```
5/minute
```

Unit = **minute**

---

## Supported Units

Limify supports several time units and their common abbreviations.

| Unit | Aliases | Seconds |
|-----|-----|-----|
| second | `second`, `seconds`, `sec`, `s` | 1 |
| minute | `minute`, `minutes`, `min`, `m` | 60 |
| hour | `hour`, `hours`, `h` | 3600 |
| day | `day`, `days`, `d` | 86400 |

Examples of valid rate formats:

```
5/second
5/sec
5/s

10/minute
10/min
10/m

100/hour
100/h

1000/day
1000/d
```

All of the above are interpreted correctly by Limify.

---

## Internal Conversion

During initialization, Limify converts rate strings into numeric values.

Example:

```
10/minute
```

becomes:

```
limit = 10
period_seconds = 60
```

These values are passed to the rate-limiting algorithm.

Example arguments passed to Redis Lua:

```
ARGV[1] = limit
ARGV[2] = period_seconds
ARGV[3] = current timestamp
```

The Lua script calculates the refill rate:

```
refill_rate = limit / period_seconds
```

This determines how quickly tokens are replenished in the token bucket.

---

## Example Rule

```python
{
    "id": "items",
    "method": "*",
    "path": "/items",
    "rate": "10/minute",
}
```

This rule allows **10 requests per minute** to `/items`.

---

## Invalid Rate Formats

The following formats are invalid:

```
10 per minute
10m
minute/10
```

Rates must always follow:

```
<number>/<unit>
```

---

## Best Practices

### Use smaller windows for APIs

Example:

```
10/second
```

This protects APIs from bursts.

---

### Use larger windows for background jobs

Example:

```
1000/hour
```

This allows high throughput while preventing abuse.

---

## Summary

Rate limits in Limify use the format:

```
<limit>/<unit>
```

Example:

```
10/minute
```

Which internally becomes:

```
limit = 10
period_seconds = 60
```

These values are then used by the Redis-backed token bucket algorithm to enforce request limits.