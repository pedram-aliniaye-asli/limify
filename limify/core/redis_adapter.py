from abc import ABC, abstractmethod
import redis
import redis.asyncio as aioredis

# ---------------- SYNC ----------------

class SyncRedisAdapter(ABC):
    @abstractmethod
    def evalsha(self, sha: str, num_keys: int, *args):
        ...

    @abstractmethod
    def script_load(self, script: str):
        ...


class RedisSyncAdapter(SyncRedisAdapter):
    def __init__(self, client: redis.Redis):
        self.client = client

    def evalsha(self, sha: str, num_keys: int, *args):
        return self.client.evalsha(sha, num_keys, *args)

    def script_load(self, script: str):
        return self.client.script_load(script)


# ---------------- ASYNC ----------------

class AsyncRedisAdapter(ABC):
    @abstractmethod
    async def evalsha(self, sha: str, num_keys: int, *args):
        ...

    @abstractmethod
    async def script_load(self, script: str):
        ...


class RedisAsyncAdapter(AsyncRedisAdapter):
    def __init__(self, client: aioredis.Redis):
        self.client = client

    async def evalsha(self, sha: str, num_keys: int, *args):
        return await self.client.evalsha(sha, num_keys, *args)

    async def script_load(self, script: str):
        return await self.client.script_load(script)
