from limify.core.rules import Rule
from limify.core.resolvers.rule_resolver import RuleResolver
from limify.core.resolvers.plan_resolver import PlanResolver
from limify.core.resolvers.key_resolver import KeyResolver
from limify.core.limiter import Limiter
from limify.defaults import DEFAULT_RULE
from limify.config import LimifyConfig

class Limify:
    def __init__(self, *, algorithm, config: LimifyConfig | None = None, rules=None, default_rule=DEFAULT_RULE, rule_resolver=None, plan_resolver=None, key_resolver=None):
        # ---- pick source of rules/default_rule
        if config is not None:
            raw_rules = config.rules
            raw_default_rule = config.default_rule
        else:
            raw_rules = rules
            raw_default_rule = default_rule

        if raw_rules is None:
            raise ValueError("Provide either config=LimifyConfig(...) or rules=[...]")

        # ---- build Rule objects (sorted by priority)
        rules_obj = Rule.rules_constructor(raw_rules)

        # ---- wire resolvers
        self.rule_resolver = rule_resolver or RuleResolver(rules_obj, raw_default_rule)
        self.plan_resolver = plan_resolver or PlanResolver()
        self.key_resolver = key_resolver or KeyResolver()

        # ---- wire limiter
        self.limiter = Limiter(
            rule_resolver=self.rule_resolver,
            plan_resolver=self.plan_resolver,
            key_resolver=self.key_resolver,
            algorithm=algorithm,
        )