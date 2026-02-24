from limify.core.rules import Rule
from limify.core.resolvers.rule_resolver import RuleResolver
from limify.core.resolvers.plan_resolver import PlanResolver
from limify.core.resolvers.key_resolver import KeyResolver
from limify.core.limiter import Limiter
from limify.defaults import DEFAULT_RULE
class Limify:
    def __init__(self, rules, algorithm, rule_resolver=None, plan_resolver=None, key_resolver=None, default_rule=DEFAULT_RULE):
        rules = Rule.rules_constructor(rules)

        self.rule_resolver = rule_resolver or RuleResolver(rules, default_rule)
        self.plan_resolver = plan_resolver or PlanResolver()
        self.key_resolver = key_resolver or KeyResolver()

        self.limiter = Limiter(
            rule_resolver=self.rule_resolver,
            plan_resolver=self.plan_resolver,
            key_resolver=self.key_resolver,
            algorithm=algorithm,
        )
