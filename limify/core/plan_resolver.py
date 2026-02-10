from limify.core.context import RequestContext
from limify.core.rules import Rule
from limify.core.plans import Plan
from limify.plan_provider import CustomPlanProvider
from limify.defaults import DEFAULT_PLAN


class PlanResolver:
    def __init__(self, plan_provider: CustomPlanProvider):
        self.plan_provider = plan_provider

    def resolve(self, context: RequestContext, rule: Rule) -> Plan:
        plan = self.plan_provider.resolve(context, rule)

        if plan:
            return plan

        return DEFAULT_PLAN
