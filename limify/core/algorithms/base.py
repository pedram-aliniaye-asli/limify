from abc import ABC, abstractmethod
from limify.core.context import RequestContext
from limify.core.plans import Plan

"""
The allow method:
Returns True if the request is allowed,
False if it should be rejected (HTTP 429) or Queued
"""


class Algorithm(ABC):
    @abstractmethod
    def allow(self, key: str, plan: Plan, context: RequestContext) -> bool:
        ...


class AsyncAlgorithm(ABC):
    @abstractmethod
    async def allow(self, key, plan, context) -> bool:
        ...