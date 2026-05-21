import json

class RuntimeIntegrationAuditor:
    def __init__(self, psm):
        self.psm = psm

    def audit(self):
        """Checks consistency across subsystems."""
        mismatches = []
        
        # Check pressure consistency
        state_pressure = self.psm.state.get("pressure", 0)
        audio_plan = self.psm.state.get("audio_plan", {})
        
        # Simple consistency check
        if state_pressure > 50 and audio_plan.get("pressure_state") == "low":
            mismatches.append("Pressure mismatch: state is high, audio is low")
            
        return mismatches
