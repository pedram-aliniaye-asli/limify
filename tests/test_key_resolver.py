from limify.core.resolvers.key_resolver import KeyResolver
from limify.core.context import RequestContext
from limify.core.rules import Rule
from limify.core.plans import Plan


def make_context(user_id=None, org_id=None, api_key=None, client_ip=None):
    return RequestContext(
        method="GET",
        path="/items",
        client_ip=client_ip,
        user_id=user_id,
        org_id=org_id,
        api_key=api_key,
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


def make_plan():
    return Plan(id="pro", limit="100/minute", period_seconds=5)

#User identity has highest priority
def test_key_resolver_user_priority():
    context = make_context(user_id=42, org_id="org1", api_key="abc", client_ip="1.1.1.1")
    rule = make_rule()

    key = KeyResolver.resolve(context, rule, None)

    assert key == "limify:items:default:user:42"

#Org fallback
def test_key_resolver_org_fallback():
    context = make_context(org_id="org1", api_key="abc", client_ip="1.1.1.1")
    rule = make_rule()

    key = KeyResolver.resolve(context, rule, None)

    assert key == "limify:items:default:org:org1"

#API key fallback
def test_key_resolver_api_key_fallback():
    context = make_context(api_key="abc123", client_ip="1.1.1.1")
    rule = make_rule()

    key = KeyResolver.resolve(context, rule, None)

    assert key == "limify:items:default:apikey:abc123"

#IP fallback
def test_key_resolver_ip_fallback():
    context = make_context(client_ip="127.0.0.1")
    rule = make_rule()

    key = KeyResolver.resolve(context, rule, None)

    assert key == "limify:items:default:ip:127.0.0.1"

#Anonymous fallback
def test_key_resolver_anonymous_fallback():
    context = make_context()
    rule = make_rule()

    key = KeyResolver.resolve(context, rule, None)

    assert key == "limify:items:default:anonymous:global"

#Plan override applied
def test_key_resolver_plan_override():
    context = make_context(user_id=1)
    rule = make_rule()
    plan = make_plan()

    key = KeyResolver.resolve(context, rule, plan)

    assert key == "limify:items:pro:user:1"

#Key structure format consistency
def test_key_structure_format():
    context = make_context(user_id=99)
    rule = make_rule()

    key = KeyResolver.resolve(context, rule, None)

    parts = key.split(":")

    assert parts[0] == "limify"
    assert parts[1] == "items"
    assert parts[2] == "default"
    assert parts[3] == "user"
    assert parts[4] == "99"
