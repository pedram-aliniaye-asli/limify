from core.context import RequestContext 
from rules import Rule

class PathMatcher:
    @staticmethod
    def match(request_context: RequestContext, rules: list[Rule]) -> Rule | None:
        """
        Returns the first Rule that matches the request_context.
        """
        req_path = request_context.path.strip("/").split("/")
        req_method = request_context.method.upper()

        for rule in rules:
            if not PathMatcher._method_matches(req_method, rule.method):
                continue
            if PathMatcher._path_matches(req_path, rule.path):
                return rule
        return None

    @staticmethod
    def _method_matches(req_method: str, rule_method: str) -> bool:
        if rule_method == "*" or rule_method.upper() == req_method:
            return True
        return False

    @staticmethod
    def _path_matches(req_segments: list[str], rule_path: str) -> bool:
        """
        Simple wildcard matching for * and **
        """
        rule_segments = rule_path.strip("/").split("/")
        return PathMatcher._match_segments(req_segments, rule_segments)

    @staticmethod
    def _match_segments(req_segments: list[str], rule_segments: list[str]) -> bool:
        i = j = 0
        while i < len(req_segments) and j < len(rule_segments):
            if rule_segments[j] == "**":
                # match rest of the path recursively
                if j + 1 == len(rule_segments):
                    return True  # ** at the end matches all
                # try to match remaining rule_segments at each possible position
                for k in range(i, len(req_segments) + 1):
                    if PathMatcher._match_segments(req_segments[k:], rule_segments[j+1:]):
                        return True
                return False
            elif rule_segments[j] == "*":
                # match exactly one segment
                i += 1
                j += 1
            elif rule_segments[j] == req_segments[i]:
                i += 1
                j += 1
            else:
                return False

        # Check remaining segments
        if i == len(req_segments) and j == len(rule_segments):
            return True
        if j < len(rule_segments) and rule_segments[j] == "**":
            return True
        return False
