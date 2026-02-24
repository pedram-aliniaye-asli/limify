import pytest
from unittest.mock import Mock, AsyncMock

from limify.core.redis_adapter import RedisSyncAdapter, RedisAsyncAdapter


#SYNC ADAPTER TESTS
def test_redis_sync_adapter_evalsha_delegates():
    client = Mock()
    client.evalsha.return_value = "OK"

    adapter = RedisSyncAdapter(client)

    result = adapter.evalsha("sha123", 1, "key1", "arg1", "arg2")

    assert result == "OK"
    client.evalsha.assert_called_once_with("sha123", 1, "key1", "arg1", "arg2")


def test_redis_sync_adapter_script_load_delegates():
    client = Mock()
    client.script_load.return_value = "sha_loaded"

    adapter = RedisSyncAdapter(client)

    result = adapter.script_load("return 1")

    assert result == "sha_loaded"
    client.script_load.assert_called_once_with("return 1")


#ASYNC ADAPTER TESTS
@pytest.mark.asyncio
async def test_redis_async_adapter_evalsha_delegates():
    client = Mock()
    client.evalsha = AsyncMock(return_value="OK")

    adapter = RedisAsyncAdapter(client)

    result = await adapter.evalsha("sha123", 1, "key1", "arg1", "arg2")

    assert result == "OK"
    client.evalsha.assert_awaited_once_with("sha123", 1, "key1", "arg1", "arg2")


@pytest.mark.asyncio
async def test_redis_async_adapter_script_load_delegates():
    client = Mock()
    client.script_load = AsyncMock(return_value="sha_loaded")

    adapter = RedisAsyncAdapter(client)

    result = await adapter.script_load("return 1")

    assert result == "sha_loaded"
    client.script_load.assert_awaited_once_with("return 1")