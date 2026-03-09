class CustomPlanProvider:
    def resolve(self, context, rule):
        return None # User should provide the logic here. Probably fetching plan details from the db.