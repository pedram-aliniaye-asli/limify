from limify.core.context import RequestContext
from limify.core.rules import Rule
from limify.core.plans import Plan
from limify.plan_provider import CustomPlanProvider
from limify.core.rate import parse_rate


class PlanResolver:
    def __init__(self, plan_provider: CustomPlanProvider):
        self.plan_provider = plan_provider

    def resolve(self, context: RequestContext, rule: Rule) -> Plan:
        # 1) Try user-provided plan
        plan = self.plan_provider.resolve(context, rule)
        if plan is not None:
            return plan

        # 2) Default plan derived from rule.rate
        r = parse_rate(rule.rate)
        return Plan(id="default", limit=r.limit, period_seconds=r.period_seconds)