from limify.core.rules import Rule
from limify.core.context import RequestContext
from limify.core.path import PathMatcher

class RuleResolver:
    def __init__(self, rules: list[Rule], default_rule: Rule | None = None):
        self.rules = rules
        self.default_rule = default_rule

    def resolve(self, context: RequestContext) -> Rule | None:
        rule = PathMatcher.match(context, self.rules)

        if rule:
            return rule

        return self.default_rule
