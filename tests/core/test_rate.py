import pytest
from limify.core.rate import parse_rate

def test_parse_rate_minute():
    r = parse_rate("10/minute")
    assert r.limit == 10
    assert r.period_seconds == 60

def test_parse_rate_invalid():
    with pytest.raises(ValueError):
        parse_rate("ten/minute")