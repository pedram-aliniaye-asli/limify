from abc import ABC, abstractmethod

class RedisAdapter(ABC):
    @abstractmethod
    def get(self, key: str):
        ...

    @abstractmethod
    def set(self, key: str, value, ex=None):
        ...

    @abstractmethod
    def evalsha(self, sha: str, num_keys: int, *args):
        ...

    @abstractmethod
    def script_load(self, script: str):
        ...


import redis
import redis.asyncio as aioredis

class SyncRedisAdapter(RedisAdapter):
    def __init__(self, client: redis.Redis):
        self.client = client

    def get(self, key: str):
        return self.client.get(key)

    def set(self, key: str, value, ex=None):
        self.client.set(key, value, ex=ex)

    def evalsha(self, sha: str, num_keys: int, *args):
        return self.client.evalsha(sha, num_keys, *args)

    def script_load(self, script: str):
        return self.client.script_load(script)

class AsyncRedisAdapter(RedisAdapter):
    def __init__(self, client: aioredis.Redis):
        self.client = client

    async def get(self, key: str):
        return await self.client.get(key)

    async def set(self, key: str, value, ex=None):
        await self.client.set(key, value, ex=ex)

    async def evalsha(self, sha: str, num_keys: int, *args):
        return await self.client.evalsha(sha, num_keys, *args)

    async def script_load(self, script: str):
        return await self.client.script_load(script)
