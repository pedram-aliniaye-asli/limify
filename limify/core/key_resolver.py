from limify.core.context import RequestContext
from limify.core.rules import Rule

class KeyResolver:
    """
    Resolves a rate-limiting key for a request.
    """

    NAMESPACE = "limify"

    @classmethod
    def resolve(cls, context: RequestContext, rule: Rule) -> str:
        """
        Returns a canonical rate-limiting key.
        """
        identity_type, identity_value = cls._resolve_identity(context)

        return cls._build_key(
            rule_id=rule.id,
            identity_type=identity_type,
            identity_value=identity_value,
        )

    # Internal KeyResolver Class Methods 

    @staticmethod
    def _resolve_identity(context: RequestContext) -> tuple[str, str]:
        """
        Determine which identity this request belongs to.
        Priority order matters.
        """

        if context.user_id:
            return "user", str(context.user_id)

        if context.org_id:
            return "org", str(context.org_id)

        if context.api_key:
            return "apikey", context.api_key

        if context.client_ip:
            return "ip", context.client_ip

        return "anonymous", "global"

    @classmethod
    def _build_key(
        cls,
        rule_id: str,
        identity_type: str,
        identity_value: str,
    ) -> str:
        return f"{cls.NAMESPACE}:{rule_id}:{identity_type}:{identity_value}"
