from limify.core.path import PathMatcher
from limify.core.rules import Rule
from limify.core.context import RequestContext


def make_context(path: str, method: str = "GET"):
    return RequestContext(
        method=method,
        path=path,
        client_ip="127.0.0.1",
        user_id=None,
        org_id=None,
        api_key=None,
    )


def make_rule(rule_id: str, method: str, path: str):
    return Rule(
        id=rule_id,
        method=method,
        path=path,
        rate="5/minute",
        burst=1,
        priority=0,
        queue=False,
    )


#Method matching
def test_method_matches_wildcard():
    assert PathMatcher._method_matches("GET", "*") is True
    assert PathMatcher._method_matches("POST", "*") is True


def test_method_matches_exact_case_insensitive():
    assert PathMatcher._method_matches("GET", "get") is True
    assert PathMatcher._method_matches("POST", "POST") is True
    assert PathMatcher._method_matches("GET", "POST") is False


#Exact path matching
def test_path_exact_match():
    assert PathMatcher._path_matches(["items"], "/items") is True
    assert PathMatcher._path_matches(["items"], "/posts") is False


def test_path_exact_match_nested():
    assert PathMatcher._path_matches(["items", "123"], "/items/123") is True
    assert PathMatcher._path_matches(["items", "123"], "/items/124") is False


#'*' wildcard (one segment)
def test_star_matches_one_segment():
    assert PathMatcher._path_matches(["items", "123"], "/items/*") is True
    assert PathMatcher._path_matches(["items"], "/items/*") is False  # needs one more segment
    assert PathMatcher._path_matches(["items", "123", "x"], "/items/*") is False  # too many segments


def test_star_in_middle():
    assert PathMatcher._path_matches(["v1", "items", "123"], "/v1/*/123") is True
    assert PathMatcher._path_matches(["v1", "posts", "123"], "/v1/*/123") is True
    assert PathMatcher._path_matches(["v1", "posts", "999"], "/v1/*/123") is False


#'**' wildcard (zero or more segments)
def test_double_star_at_end_matches_any_depth():
    assert PathMatcher._path_matches(["items"], "/**") is True
    assert PathMatcher._path_matches(["items", "123"], "/**") is True
    assert PathMatcher._path_matches(["a", "b", "c"], "/**") is True


def test_double_star_matches_zero_segments_in_middle():
    # /api/**/health should match /api/health (zero segments between)
    assert PathMatcher._path_matches(["api", "health"], "/api/**/health") is True


def test_double_star_matches_many_segments_in_middle():
    assert PathMatcher._path_matches(["api", "v1", "internal", "health"], "/api/**/health") is True
    assert PathMatcher._path_matches(["api", "v1", "health"], "/api/**/health") is True


def test_double_star_requires_suffix_match():
    # Must end with "health"
    assert PathMatcher._path_matches(["api", "v1", "status"], "/api/**/health") is False


def test_double_star_only_remaining_segments():
    # rule ends with **, matches whatever remains (including nothing)
    assert PathMatcher._path_matches(["api"], "/api/**") is True
    assert PathMatcher._path_matches(["api", "v1", "x"], "/api/**") is True
    assert PathMatcher._path_matches(["apix", "v1"], "/api/**") is False


#match(): chooses first matching rule
def test_match_returns_first_matching_rule_in_order():
    rules = [
        make_rule("default", "*", "/**"),         # matches everything
        make_rule("items", "*", "/items"),        # more specific but later
    ]

    #Because match() returns first match, this should be "default"
    result = PathMatcher.match(make_context("/items"), rules)
    assert result.id == "default"


def test_match_returns_specific_rule_if_ordered_first():
    rules = [
        make_rule("items", "*", "/items"),
        make_rule("default", "*", "/**"),
    ]

    result = PathMatcher.match(make_context("/items"), rules)
    assert result.id == "items"


def test_match_respects_method_filter():
    rules = [
        make_rule("post_items", "POST", "/items"),
        make_rule("default", "*", "/**"),
    ]

    #GET /items should not match POST rule; falls to default
    result = PathMatcher.match(make_context("/items", "GET"), rules)
    assert result.id == "default"

    #POST /items should match the POST rule
    result = PathMatcher.match(make_context("/items", "POST"), rules)
    assert result.id == "post_items"