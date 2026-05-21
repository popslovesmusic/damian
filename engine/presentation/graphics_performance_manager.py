import json

class GraphicsPerformanceManager:
    def __init__(self, contract_path, budget_path, metrics_path):
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        with open(budget_path, 'r') as f:
            self.budget = json.load(f)
        with open(metrics_path, 'r') as f:
            self.metrics = json.load(f)
        self.usage = {"effects": 0, "entities": 0, "fog": 0}

    def report_usage(self, category, amount):
        if category in self.usage:
            self.usage[category] += amount

    def check_budget(self):
        """Returns True if within budget."""
        return (self.usage["effects"] <= self.budget["max_dynamic_effects"] and
                self.usage["entities"] <= self.budget["max_animated_entities"])

    def reset_frame_usage(self):
        self.usage = {"effects": 0, "entities": 0, "fog": 0}
