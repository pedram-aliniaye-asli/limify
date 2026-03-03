import pytest
from types import SimpleNamespace
from unittest.mock import Mock, AsyncMock

from limify.core.limiter import Limiter, LimitationResult
from limify.core.context import RequestContext
from limify.core.rules import Rule
from limify.core.plans import Plan


def make_context():
    return RequestContext(
        method="GET",
        path="/items",
        client_ip="127.0.0.1",
        user_id=None,
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
        queue=False,
    )


def make_plan():
    return Plan(id="pro", limit=100, period_seconds=5)


@pytest.mark.asyncio
async def test_limiter_returns_unlimited_when_no_rule():
    context = make_context()

    rule_resolver = Mock()
    rule_resolver.resolve.return_value = None

    plan_resolver = Mock()
    key_resolver = Mock()

    algorithm = SimpleNamespace()
    algorithm.allow = AsyncMock()

    limiter = Limiter(rule_resolver, plan_resolver, key_resolver, algorithm)

    result = await limiter.check(context)

    assert isinstance(result, LimitationResult)
    assert result.allowed is True
    assert result.remaining == -1
    assert result.limit == -1
    assert result.reset_after == 0

    # Ensure no other components were called
    rule_resolver.resolve.assert_called_once_with(context)
    plan_resolver.resolve.assert_not_called()
    key_resolver.resolve.assert_not_called()
    algorithm.allow.assert_not_called()


@pytest.mark.asyncio
async def test_limiter_calls_dependencies_and_returns_algorithm_result():
    context = make_context()
    rule = make_rule()
    plan = make_plan()

    rule_resolver = Mock()
    rule_resolver.resolve.return_value = rule

    plan_resolver = Mock()
    plan_resolver.resolve.return_value = plan

    key_resolver = Mock()
    key_resolver.resolve.return_value = "limify:items:pro:ip:127.0.0.1"

    expected = LimitationResult(
        allowed=True,
        remaining=4,
        limit=5,
        reset_after=60,
    )

    algorithm = SimpleNamespace()
    algorithm.allow = AsyncMock(return_value=expected)

    limiter = Limiter(rule_resolver, plan_resolver, key_resolver, algorithm)

    result = await limiter.check(context)

    assert result == expected

    rule_resolver.resolve.assert_called_once_with(context)
    plan_resolver.resolve.assert_called_once_with(context, rule)
    key_resolver.resolve.assert_called_once_with(context, rule, plan)
    algorithm.allow.assert_awaited_once_with("limify:items:pro:ip:127.0.0.1", plan, context)


@pytest.mark.asyncio
async def test_limiter_propagates_blocked_result():
    context = make_context()
    rule = make_rule()
    plan = make_plan()

    rule_resolver = Mock()
    rule_resolver.resolve.return_value = rule

    plan_resolver = Mock()
    plan_resolver.resolve.return_value = plan

    key_resolver = Mock()
    key_resolver.resolve.return_value = "limify:items:pro:ip:127.0.0.1"

    expected = LimitationResult(
        allowed=False,
        remaining=0,
        limit=5,
        reset_after=30,
    )

    algorithm = SimpleNamespace()
    algorithm.allow = AsyncMock(return_value=expected)

    limiter = Limiter(rule_resolver, plan_resolver, key_resolver, algorithm)

    result = await limiter.check(context)

    assert result.allowed is False
    assert result.remaining == 0
    assert result.limit == 5
    assert result.reset_after == 30