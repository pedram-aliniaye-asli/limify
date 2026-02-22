from dataclasses import dataclass


@dataclass
class LimitationResult:
    allowed: bool
    remaining: int
    limit: int
    reset_after: int


class Limiter:
    def __init__(self, rule_resolver, plan_resolver, key_resolver, algorithm):
        self.rule_resolver = rule_resolver
        self.plan_resolver = plan_resolver
        self.key_resolver = key_resolver
        self.algorithm = algorithm

    async def check(self, context):
        #Resolve rule
        rule = self.rule_resolver.resolve(context)

        if not rule:
            # No rate limit rule
            return LimitationResult(
                allowed=True,
                remaining=-1,
                limit=-1,
                reset_after=0,
            )

        #Resolve plan
        plan = self.plan_resolver.resolve(context, rule)

        #Resolve key
        key = self.key_resolver.resolve(context, rule, plan) 

        #Call algorithm
        result = await self.algorithm.allow(key, plan, context)

        return result # result contains allowed + remaining + limit + reset_after
# TO-DO check why in redis it's like that all keys are being called by each request instead of just one