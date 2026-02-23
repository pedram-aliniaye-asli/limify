from unittest.mock import Mock
from limify.core.resolvers.plan_resolver import PlanResolver
from limify.core.context import RequestContext
from limify.core.rules import Rule
from limify.core.plans import Plan
from limify.defaults import DEFAULT_PLAN

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

#Returns provider plan if exists
def test_plan_resolver_returns_provider_plan():
    context = make_context()
    rule = make_rule()

    custom_plan = Plan(id="pro", limit="100/minute", period_seconds=5)

    mock_provider = Mock()
    mock_provider.resolve.return_value = custom_plan

    resolver = PlanResolver(mock_provider)

    result = resolver.resolve(context, rule)

    assert result == custom_plan
    mock_provider.resolve.assert_called_once_with(context, rule)


# ---------------------------------------
# 2️⃣ Falls back to DEFAULT_PLAN
# ---------------------------------------

def test_plan_resolver_falls_back_to_default():
    context = make_context()
    rule = make_rule()

    mock_provider = Mock()
    mock_provider.resolve.return_value = None

    resolver = PlanResolver(mock_provider)

    result = resolver.resolve(context, rule)

    assert result == DEFAULT_PLAN
    mock_provider.resolve.assert_called_once_with(context, rule)


# ---------------------------------------
# 3️⃣ DEFAULT_PLAN is actually returned (identity check)
# ---------------------------------------

def test_plan_resolver_returns_exact_default_instance():
    context = make_context()
    rule = make_rule()

    mock_provider = Mock()
    mock_provider.resolve.return_value = None

    resolver = PlanResolver(mock_provider)

    result = resolver.resolve(context, rule)

    assert result is DEFAULT_PLAN