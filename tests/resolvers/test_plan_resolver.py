from unittest.mock import Mock

from limify.core.resolvers.plan_resolver import PlanResolver
from limify.core.context import RequestContext
from limify.core.rules import Rule
from limify.core.plans import Plan


def make_context():
    return RequestContext(
        method="GET",
        path="/items",
        client_ip="127.0.0.1",
        user_id=1,
        org_id=None,
        api_key=None,
    )


def make_rule():
    return Rule(
        id="items",
        method="*",
        path="/items",
        rate="5/minute",
        burst=1,
        priority=10,
    )


# Returns provider plan if exists
def test_plan_resolver_returns_provider_plan():
    context = make_context()
    rule = make_rule()

    custom_plan = Plan(id="pro", limit=100, period_seconds=5)

    mock_provider = Mock()
    mock_provider.resolve.return_value = custom_plan

    resolver = PlanResolver(mock_provider)

    result = resolver.resolve(context, rule)

    assert result == custom_plan
    mock_provider.resolve.assert_called_once_with(context, rule)


# Falls back to rule-derived plan when provider returns None
def test_plan_resolver_builds_plan_from_rule_rate():
    context = make_context()
    rule = make_rule()

    mock_provider = Mock()
    mock_provider.resolve.return_value = None

    resolver = PlanResolver(mock_provider)

    result = resolver.resolve(context, rule)

    # "5/minute" → limit=5, period_seconds=60
    assert result.limit == 5
    assert result.period_seconds == 60
    assert result.id == "default"

    mock_provider.resolve.assert_called_once_with(context, rule)