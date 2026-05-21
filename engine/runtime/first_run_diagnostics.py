import os
import json

class FirstRunDiagnostics:
    def __init__(self, contract_path):
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
            
    def run_checks(self):
        """Performs startup diagnostics."""
        results = {"passed": True, "errors": []}
        
        # Check TOWER_DATA
        if not os.environ.get("TOWER_DATA_PATH") and not os.path.exists("tower_data"):
            results["passed"] = False
            results["errors"].append("ERR_001: Missing TOWER_DATA")
            
        return results
