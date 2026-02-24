from limify.core.rules import Rule
from limify.core.context import RequestContext
from limify.core.resolvers.rule_resolver import RuleResolver

def make_rules():
    user_rules = [
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
            "rate": "5/minute",
            "priority": 10,
        },
    ]
    return Rule.rules_constructor(user_rules)

def make_context(path: str, method: str = "GET") -> RequestContext:
    return RequestContext(
        method=method,
        path=path,
        client_ip="127.0.0.1",
        user_id=None,
        org_id=None,
        api_key=None,
    )
#Matches specific rule
def test_rule_resolver_matches_specific_rule():
    rules = make_rules()
    resolver = RuleResolver(rules, default_rule=rules[0])

    context = make_context("/items", "GET")
    result = resolver.resolve(context)

    assert result.id == "items"  # high priority rule matches first

#Falls back to default_rule
def test_rule_resolver_falls_back_to_default():
    rules = make_rules()
    resolver = RuleResolver(rules, default_rule=rules[0])

    context = make_context("/unknown", "GET")
    result = resolver.resolve(context)

    assert result.id == "default"  # no match → fallback

#Returns None if no match and no default
def test_rule_resolver_returns_none_if_no_match_and_no_default():
    rules = make_rules()
    # remove default from rules list
    rules_without_default = [r for r in rules if r.id != "default"]
    resolver = RuleResolver(rules_without_default, default_rule=None)

    context = make_context("/unknown", "GET")
    result = resolver.resolve(context)

    assert result is None  # no match, no default → None

#Matches with wildcard **
def test_rule_resolver_matches_wildcard_path():
    rules = make_rules()
    resolver = RuleResolver(rules, default_rule=None)

    context = make_context("/any/deep/path", "GET")
    result = resolver.resolve(context)

    # matches default rule because of /** wildcard
    assert result.id == "default"


# TO-DO: Continue adding unit tests