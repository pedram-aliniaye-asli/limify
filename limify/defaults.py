from limify.core.rules import Rule


DEFAULT_PLAN = None

DEFAULT_RULE = Rule(
    id="default",
    method="*",
    path="/**",
    rate="100/minute",
    burst=1,
    priority=-999
)
