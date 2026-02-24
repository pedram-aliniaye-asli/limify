import pytest
from unittest.mock import Mock, AsyncMock
from redis.exceptions import NoScriptError

from limify.core.limiter import LimitationResult
from limify.core.context import RequestContext
from limify.core.plans import Plan

from limify.core.algorithms.token_bucket import TokenBucketAlgorithm, AsyncTokenBucketAlgorithm  # adjust import


def make_context():
    return RequestContext(
        method="GET",
        path="/items",
        client_ip="127.0.0.1",
        user_id=None,
        org_id=None,
        api_key=None,
    )


def make_plan(limit=5, period_seconds=60):
    return Plan(id="default", limit=limit, period_seconds=period_seconds)


# SYNC TokenBucketAlgorithm
def test_sync_algorithm_loads_script_on_init(monkeypatch):
    redis_adapter = Mock()
    redis_adapter.script_load.return_value = "sha1"

    algo = TokenBucketAlgorithm(redis_adapter)

    assert algo.sha == "sha1"
    redis_adapter.script_load.assert_called_once()
    # not calling evalsha yet
    redis_adapter.evalsha.assert_not_called()


def test_sync_algorithm_allow_calls_evalsha_with_expected_args(monkeypatch):
    # freeze time.time() to deterministic value
    monkeypatch.setattr("limify.core.algorithms.token_bucket.time.time", lambda: 1700000000)

    redis_adapter = Mock()
    redis_adapter.script_load.return_value = "sha1"
    redis_adapter.evalsha.return_value = (1, 4, 0)  # allowed, remaining, reset_after

    algo = TokenBucketAlgorithm(redis_adapter)

    plan = make_plan(limit=5, period_seconds=60)
    context = make_context()

    result = algo.allow("limify:key", plan, context)

    assert isinstance(result, LimitationResult)
    assert result.allowed is True
    assert result.remaining == 4
    assert result.limit == 5
    assert result.reset_after == 0

    redis_adapter.evalsha.assert_called_once_with(
        "sha1", 1, "limify:key", plan.limit, plan.period_seconds, 1700000000
    )


def test_sync_algorithm_reloads_script_on_noscript(monkeypatch):
    monkeypatch.setattr("limify.core.algorithms.token_bucket.time.time", lambda: 1700000000)

    redis_adapter = Mock()
    redis_adapter.script_load.side_effect = ["sha1", "sha2"]
    redis_adapter.evalsha.side_effect = [
        NoScriptError("NOSCRIPT"),  # first call fails
        (1, 4, 0),                  # second succeeds
    ]

    algo = TokenBucketAlgorithm(redis_adapter)
    plan = make_plan(limit=5, period_seconds=60)
    context = make_context()

    result = algo.allow("limify:key", plan, context)

    assert result.allowed is True
    assert result.remaining == 4
    assert result.limit == 5
    assert result.reset_after == 0

    # script_load called once in __init__ and once on NoScriptError
    assert redis_adapter.script_load.call_count == 2

    # evalsha called twice (first raises, second succeeds)
    assert redis_adapter.evalsha.call_count == 2

    # second evalsha uses the refreshed sha2
    redis_adapter.evalsha.assert_called_with(
        "sha2", 1, "limify:key", plan.limit, plan.period_seconds, 1700000000
    )


def test_sync_algorithm_returns_blocked_result(monkeypatch):
    monkeypatch.setattr("limify.core.algorithms.token_bucket.time.time", lambda: 1700000000)

    redis_adapter = Mock()
    redis_adapter.script_load.return_value = "sha1"
    redis_adapter.evalsha.return_value = (0, 0, 12)  # blocked

    algo = TokenBucketAlgorithm(redis_adapter)
    plan = make_plan(limit=5, period_seconds=60)
    context = make_context()

    result = algo.allow("limify:key", plan, context)

    assert result.allowed is False
    assert result.remaining == 0
    assert result.limit == 5
    assert result.reset_after == 12


# ASYNC AsyncTokenBucketAlgorithm
@pytest.mark.asyncio
async def test_async_algorithm_initialize_loads_script(monkeypatch):
    redis_adapter = Mock()
    redis_adapter.script_load = AsyncMock(return_value="shaA")

    algo = AsyncTokenBucketAlgorithm(redis_adapter)
    assert algo.sha is None

    await algo.initialize()

    assert algo.sha == "shaA"
    redis_adapter.script_load.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_algorithm_allow_calls_evalsha_with_expected_args(monkeypatch):
    monkeypatch.setattr("limify.core.algorithms.token_bucket.time.time", lambda: 1700000000)

    redis_adapter = Mock()
    redis_adapter.script_load = AsyncMock(return_value="shaA")
    redis_adapter.evalsha = AsyncMock(return_value=(1, 4, 0))

    algo = AsyncTokenBucketAlgorithm(redis_adapter)
    await algo.initialize()

    plan = make_plan(limit=5, period_seconds=60)
    context = make_context()

    result = await algo.allow("limify:key", plan, context)

    assert result.allowed is True
    assert result.remaining == 4
    assert result.limit == 5
    assert result.reset_after == 0

    redis_adapter.evalsha.assert_awaited_once_with(
        "shaA", 1, "limify:key", plan.limit, plan.period_seconds, 1700000000
    )


@pytest.mark.asyncio
async def test_async_algorithm_reloads_script_on_noscript(monkeypatch):
    monkeypatch.setattr("limify.core.algorithms.token_bucket.time.time", lambda: 1700000000)

    redis_adapter = Mock()
    redis_adapter.script_load = AsyncMock(side_effect=["shaA", "shaB"])
    redis_adapter.evalsha = AsyncMock(side_effect=[
        NoScriptError("NOSCRIPT"),
        (1, 4, 0),
    ])

    algo = AsyncTokenBucketAlgorithm(redis_adapter)
    await algo.initialize()

    plan = make_plan(limit=5, period_seconds=60)
    context = make_context()

    result = await algo.allow("limify:key", plan, context)

    assert result.allowed is True
    assert result.remaining == 4
    assert result.limit == 5
    assert result.reset_after == 0

    # evalsha awaited twice
    assert redis_adapter.evalsha.await_count == 2

    # script_load awaited twice (initialize + reload)
    assert redis_adapter.script_load.await_count == 2

    # second evalsha uses refreshed shaB
    redis_adapter.evalsha.assert_awaited_with(
        "shaB", 1, "limify:key", plan.limit, plan.period_seconds, 1700000000
    )


@pytest.mark.asyncio
async def test_async_algorithm_returns_blocked_result(monkeypatch):
    monkeypatch.setattr("limify.core.algorithms.token_bucket.time.time", lambda: 1700000000)

    redis_adapter = Mock()
    redis_adapter.script_load = AsyncMock(return_value="shaA")
    redis_adapter.evalsha = AsyncMock(return_value=(0, 0, 7))

    algo = AsyncTokenBucketAlgorithm(redis_adapter)
    await algo.initialize()

    plan = make_plan(limit=5, period_seconds=60)
    context = make_context()

    result = await algo.allow("limify:key", plan, context)

    assert result.allowed is False
    assert result.remaining == 0
    assert result.limit == 5
    assert result.reset_after == 7