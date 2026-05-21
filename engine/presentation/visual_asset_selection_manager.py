import json

class VisualAssetSelectionManager:
    def __init__(self, contract_path, approved_set_path, log_path, rules_path):
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        with open(approved_set_path, 'r') as f:
            self.approved_set = json.load(f)
        with open(log_path, 'r') as f:
            self.rejected_log = json.load(f)
        with open(rules_path, 'r') as f:
            self.consistency_rules = json.load(f)
        self.log_path = log_path

    def is_asset_approved(self, category, asset_id):
        """Checks if an asset is in the approved set."""
        if category not in self.approved_set:
            return False
        return asset_id in self.approved_set[category]

    def log_rejection(self, category, asset_id, reason):
        """Logs rejected assets."""
        self.rejected_log.append({
            "category": category,
            "asset_id": asset_id,
            "reason": reason
        })
        with open(self.log_path, 'w') as f:
            json.dump(self.rejected_log, f, indent=2)
