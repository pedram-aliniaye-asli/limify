# Plans

Limify supports **plan-based rate limiting**, which makes it suitable for SaaS platforms, APIs, and multi-tier systems.

A **plan** defines the numeric rate limit that will actually be enforced for a request.

Example plans:

```text
free       → 10/minute
pro        → 100/minute
enterprise → 1000/minute
```

This allows different users, organizations, or API consumers to receive different rate limits based on subscription tier or account type.

---

## Why Plans Exist

Rules determine:

- which requests match
- which endpoints are affected
- the default rate definition

Plans determine:

- the actual limit applied to the request
- the time period used by the algorithm
- the plan identity included in the Redis key

This separation is important because two requests may match the **same rule** but still receive **different limits** depending on the user or organization plan.

For example:

- `GET /items` by a free user → `10/minute`
- `GET /items` by a pro user → `100/minute`

Same endpoint, same rule, different plan.

---

## Plan Structure

Internally, a plan contains:

- `id`
- `limit`
- `period_seconds`

Example:

```python
Plan(
    id="pro",
    limit=100,
    period_seconds=60,
)
```

This means:

- plan name = `pro`
- 100 requests allowed
- every 60 seconds

The algorithm operates on these numeric values.

---

## Relationship Between Rules and Plans

A rule contains a human-readable rate string such as:

```python
{
    "id": "items",
    "method": "*",
    "path": "/items",
    "rate": "10/minute",
}
```

If no custom plan provider is used, Limify derives a default plan from the rule rate.

Example:

```text
10/minute
```

becomes:

```python
Plan(
    id="default",
    limit=10,
    period_seconds=60,
)
```

So the rule provides the fallback rate limit.

---

## Default Behavior

If no custom `PlanProvider` returns a plan, Limify automatically creates a plan from the rule’s `rate`.

Example:

Rule:

```python
{
    "id": "items",
    "method": "*",
    "path": "/items",
    "rate": "10/minute",
}
```

Derived plan:

```python
Plan(
    id="default",
    limit=10,
    period_seconds=60,
)
```

This makes plans optional for simple use cases.

---

## Custom PlanProvider

For SaaS or multi-tenant systems, you can provide your own `PlanProvider`.

A custom provider can decide the plan dynamically based on:

- user ID
- organization ID
- API key
- database records
- billing tier
- feature flags

Example interface:

```python
class CustomPlanProvider:
    def resolve(self, context, rule):
        pass
```

The provider receives:

- `context` → request metadata
- `rule` → the matched rule

It should return either:

- a `Plan`
- or `None` to fall back to the rule-derived default plan

---

## Example PlanProvider

Below is a simple example of a custom provider:

```python
from limify.core.plans import Plan


class CustomPlanProvider:
    def resolve(self, context, rule):
        # Example only: replace with database or service lookup
        if context.user_id == 1:
            return Plan(id="enterprise", limit=1000, period_seconds=60)

        if context.user_id == 2:
            return Plan(id="pro", limit=100, period_seconds=60)

        return None
```

Behavior:

- user 1 → enterprise plan
- user 2 → pro plan
- everyone else → default plan derived from `rule.rate`

---

## Example With Organization-Based Plans

Plans are especially useful for multi-tenant SaaS systems.

Example:

```python
from limify.core.plans import Plan


class CustomPlanProvider:
    def resolve(self, context, rule):
        if context.org_id == "acme":
            return Plan(id="enterprise", limit=1000, period_seconds=60)

        if context.org_id == "startup":
            return Plan(id="pro", limit=100, period_seconds=60)

        return None
```

In this example:

- organization `acme` gets enterprise limits
- organization `startup` gets pro limits
- all others fall back to the rule-defined rate

---

## How Plans Affect Redis Keys

Plans are included in the Redis key.

Format:

```text
limify:{rule_id}:{plan_id}:{identity_type}:{identity_value}
```

Examples:

```text
limify:items:free:user:42
limify:items:pro:user:42
limify:items:enterprise:user:42
```

This is important because each plan gets its own independent bucket.

If a user upgrades from `free` to `pro`, they will use a different Redis key.

---

## Example End-to-End Flow

Suppose the rule is:

```python
{
    "id": "items",
    "method": "*",
    "path": "/items",
    "rate": "10/minute",
}
```

And the request context is:

```python
RequestContext(
    method="GET",
    path="/items",
    user_id=2,
    org_id=None,
    api_key=None,
    client_ip="127.0.0.1",
)
```

Custom provider:

```python
if context.user_id == 2:
    return Plan(id="pro", limit=100, period_seconds=60)
```

Result:

- matched rule = `items`
- resolved plan = `pro`
- key = `limify:items:pro:user:2`
- effective limit = `100/minute`

So even though the rule says `10/minute`, the custom plan overrides it.

---

## When to Use Custom Plans

Use a custom `PlanProvider` when:

- users have subscription tiers
- organizations have different quotas
- API keys map to different products
- you want billing-based or account-based limits

Use only rule-derived plans when:

- all traffic should have the same rate limit
- you want simple endpoint-based throttling
- there is no account or tier differentiation

---

## Summary

Plans define the **effective numeric rate limit** applied to a request.

They allow Limify to support:

- subscription tiers
- organization-level quotas
- API products
- multi-tenant SaaS systems

If no custom plan is provided, Limify derives a default plan from the matched rule’s `rate`.

A custom `PlanProvider` can override that behavior and return a plan dynamically based on request context.