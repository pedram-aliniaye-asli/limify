from dataclasses import dataclass

@dataclass(frozen=True)
class Rule:
    id: str
    method: str
    path: str
    rate: str
    burst: int = 1
    priority: int = 0

    @staticmethod
    def rules_constructor(user_rules) -> list:
        # convert to Rule objects
        rules = [
            Rule(
                id=r["id"],
                method=r["method"],
                path=r["path"],
                rate=str(r["rate"]),
                burst=int(r.get("burst", 1)),
                priority=int(r.get("priority", 0))
            )
            for r in user_rules
        ]

        # sort by priority descending
        rules.sort(key=lambda r: r.priority, reverse=True)
        return(rules)



#User defined rules
user_rules = [
    {
        "id": "items_list",
        "method": "GET",
        "path": "/items/*",
        "rate": "10/min",
        "burst": 2,
        "priority": 10
    },

]