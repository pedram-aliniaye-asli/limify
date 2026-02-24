from limify.core.rules import Rule


def test_rules_constructor_converts_dicts_to_rules():
    user_rules = [
        {"id": "a", "method": "GET", "path": "/a", "rate": "5/minute"},
        {"id": "b", "method": "*", "path": "/b", "rate": 10},  # rate as int -> str
    ]

    rules = Rule.rules_constructor(user_rules)

    assert all(isinstance(r, Rule) for r in rules)

    assert rules[0].id in {"a", "b"}  # sorted may change order if same priority
    assert rules[1].id in {"a", "b"}

    # rate always string
    assert isinstance(rules[0].rate, str)
    assert isinstance(rules[1].rate, str)


def test_rules_constructor_applies_defaults():
    user_rules = [
        {"id": "x", "method": "*", "path": "/x", "rate": "5/minute"},
    ]

    rules = Rule.rules_constructor(user_rules)
    r0 = rules[0]

    assert r0.burst == 1
    assert r0.priority == 0
    assert r0.queue is False


def test_rules_constructor_casts_types():
    user_rules = [
        {
            "id": "x",
            "method": "*",
            "path": "/x",
            "rate": 5,          # becomes "5"
            "burst": "2",       # becomes 2
            "priority": "10",   # becomes 10
            "queue": True
        },
    ]

    rules = Rule.rules_constructor(user_rules)
    r0 = rules[0]

    assert r0.rate == "5"
    assert r0.burst == 2
    assert r0.priority == 10
    assert r0.queue is True


def test_rules_constructor_sorts_by_priority_descending():
    user_rules = [
        {"id": "low", "method": "*", "path": "/low", "rate": "1/minute", "priority": 0},
        {"id": "mid", "method": "*", "path": "/mid", "rate": "1/minute", "priority": 5},
        {"id": "high", "method": "*", "path": "/high", "rate": "1/minute", "priority": 10},
    ]

    rules = Rule.rules_constructor(user_rules)

    assert [r.id for r in rules] == ["high", "mid", "low"]


def test_rules_constructor_keeps_same_priority_ordering_stable_enough():
    # Python sort is stable: if priority is equal, original order is preserved.
    user_rules = [
        {"id": "first", "method": "*", "path": "/1", "rate": "1/minute", "priority": 5},
        {"id": "second", "method": "*", "path": "/2", "rate": "1/minute", "priority": 5},
    ]

    rules = Rule.rules_constructor(user_rules)

    assert [r.id for r in rules] == ["first", "second"]