import json

class PlaytestTelemetryManager:
    def __init__(self, contract_path, metrics_path, heatmap_path, confusion_path):
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        with open(metrics_path, 'r') as f:
            self.metrics_profile = json.load(f)
        with open(heatmap_path, 'r') as f:
            self.heatmap_rules = json.load(f)
        with open(confusion_path, 'r') as f:
            self.confusion_rules = json.load(f)
            
        self.telemetry_data = []

    def capture_event(self, event_type, details):
        """Captures a telemetry event."""
        if not self.contract.get("enabled", True):
            return
            
        entry = {"event": event_type, "details": details}
        self.telemetry_data.append(entry)
        
    def save_telemetry(self):
        with open(self.contract.get("audit_path", "telemetry.json"), 'w') as f:
            json.dump(self.telemetry_data, f, indent=2)
