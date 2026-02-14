import time
from redis.exceptions import NoScriptError
from limify.core.algorithms.base import Algorithm
from limify.core.plans import Plan
from limify.core.context import RequestContext
from limify.core.redis_adapter import SyncRedisAdapter, AsyncRedisAdapter


class TokenBucketAlgorithm(Algorithm):
    LUA_SCRIPT = """
    -- KEYS[1] = token bucket key
    -- ARGV[1] = limit
    -- ARGV[2] = period_seconds
    -- ARGV[3] = now (timestamp)
    local bucket = redis.call("GET", KEYS[1])
    local tokens, last
    if bucket then
        local parts = {}
        for part in string.gmatch(bucket, "[^:]+") do
            table.insert(parts, part)
        end
        tokens = tonumber(parts[1])
        last = tonumber(parts[2])
        local refill = (tonumber(ARGV[3]) - last) * (tonumber(ARGV[1]) / tonumber(ARGV[2]))
        tokens = math.min(tonumber(ARGV[1]), tokens + refill)
    else
        tokens = tonumber(ARGV[1])
    end
    if tokens >= 1 then
        tokens = tokens - 1
        redis.call("SET", KEYS[1], tokens .. ":" .. ARGV[3])
        return 1
    else
        return 0
    end
    """
    def __init__(self, redis: SyncRedisAdapter):
        self.redis = redis
        self.sha = self.redis.script_load(self.LUA_SCRIPT)

    def allow(self, key: str, plan: Plan, context: RequestContext) -> bool:
        now = int(time.time())

        try:
            allowed = self.redis.evalsha(
                self.sha, 1, key, plan.limit, plan.period_seconds, now
            )
        except NoScriptError:
            self.sha = self.redis.script_load(self.LUA_SCRIPT)
            allowed = self.redis.evalsha(
                self.sha, 1, key, plan.limit, plan.period_seconds, now
            )

        return bool(allowed)



class AsyncTokenBucketAlgorithm:
    LUA_SCRIPT = """
    -- KEYS[1] = token bucket key
    -- ARGV[1] = limit
    -- ARGV[2] = period_seconds
    -- ARGV[3] = now (timestamp)
    local bucket = redis.call("GET", KEYS[1])
    local tokens, last
    if bucket then
        local parts = {}
        for part in string.gmatch(bucket, "[^:]+") do
            table.insert(parts, part)
        end
        tokens = tonumber(parts[1])
        last = tonumber(parts[2])
        local refill = (tonumber(ARGV[3]) - last) * (tonumber(ARGV[1]) / tonumber(ARGV[2]))
        tokens = math.min(tonumber(ARGV[1]), tokens + refill)
    else
        tokens = tonumber(ARGV[1])
    end
    if tokens >= 1 then
        tokens = tokens - 1
        redis.call("SET", KEYS[1], tokens .. ":" .. ARGV[3])
        return 1
    else
        return 0
    end
    """
    def __init__(self, redis: AsyncRedisAdapter):
        self.redis = redis
        self.sha = None

    async def initialize(self):
        self.sha = await self.redis.script_load(self.LUA_SCRIPT)

    async def allow(self, key: str, plan: Plan, context: RequestContext) -> bool:
        now = int(time.time())

        try:
            allowed = await self.redis.evalsha(
                self.sha, 1, key, plan.limit, plan.period_seconds, now
            )
        except NoScriptError:
            self.sha = await self.redis.script_load(self.LUA_SCRIPT)
            allowed = await self.redis.evalsha(
                self.sha, 1, key, plan.limit, plan.period_seconds, now
            )

        return bool(allowed)
