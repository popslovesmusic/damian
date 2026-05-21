import os
import json

class VisualScaffoldManager:
    def __init__(self, contract_path, hud_profile_path, asset_manifest_path):
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        with open(hud_profile_path, 'r') as f:
            self.hud_profile = json.load(f)
        with open(asset_manifest_path, 'r') as f:
            self.asset_manifest = json.load(f)

    def _get_asset_repr(self, asset_key):
        return self.asset_manifest["assets"].get(asset_key, {}).get("representation", "?")

    def _generate_health_bar(self, health):
        bar_length = 10
        filled = int(health / 100 * bar_length)
        empty = bar_length - filled
        return f"Health: [{self._get_asset_repr('hud_health_full')[:filled]}{self._get_asset_repr('hud_health_empty')[:empty]}]"

    def _generate_stamina_bar(self, stamina):
        bar_length = 10
        filled = int(stamina / 100 * bar_length)
        empty = bar_length - filled
        return f"Stam: [{self._get_asset_repr('hud_health_full')[:filled]}{self._get_asset_repr('hud_health_empty')[:empty]}]" # Re-using for simplicity

    def _generate_pressure_indicator(self, pressure):
        if pressure > self.hud_profile["elements"]["pressure_indicator"]["high_threshold"]:
            return f"Pressure: {self._get_asset_repr('hud_pressure_high')}"
        elif pressure > 30: # Assuming 30 is medium threshold
            return f"Pressure: {self._get_asset_repr('hud_pressure_medium')}"
        else:
            return f"Pressure: {self._get_asset_repr('hud_pressure_low')}"

    def _generate_resource_counts(self, resources):
        res_strs = []
        for r_type, count in resources.items():
            res_strs.append(f"{r_type[:1].upper()}{r_type[1:].lower()}: {count}")
        return ", ".join(res_strs)

    def generate_hud_output(self, game_state):
        """Generates a minimal HUD representation."""
        hud_lines = []
        hud_lines.append(self._generate_health_bar(game_state["health"]))
        hud_lines.append(self._generate_stamina_bar(game_state["stamina"]))
        hud_lines.append(self._generate_pressure_indicator(game_state["pressure"]))
        hud_lines.append(self._generate_resource_counts(game_state["resources"]))
        hud_lines.append(f"Location: {game_state['location']}")
        hud_lines.append(f"Audio: {game_state.get('audio_state', 'No Audio')}") # NEW
        
        return "\n".join(hud_lines)

    def generate_map_layout(self, game_state):
        """Generates a simple ASCII map layout."""
        # This is a very simplified static map for illustration
        player_x, player_y = 2, 2 # Assuming player is always at 2,2 for simplicity
        
        layout = [
            list("##########"),
            list("#........#"),
            list("#........#"),
            list("#........#"),
            list("##########")
        ]
        
        layout[player_y][player_x] = self._get_asset_repr('character_player')
        
        # Add a placeholder enemy
        if game_state["location"].startswith("Moved"): # Simulate enemy appearing after movement
            layout[1][4] = self._get_asset_repr('enemy_generic')
        
        # Add a placeholder resource
        if game_state["resources"].get("FOOD", 0) < 50: # If food is low, maybe a resource appears
             layout[3][1] = self._get_asset_repr('resource_item')

        return "\n".join(["".join(row) for row in layout])

    def generate_death_screen(self, final_state, manifest):
        """Generates a text-based death/recovery screen."""
        if final_state["has_died"]:
            screen_output = [
                "------------------------------------",
                "           YOU ARE DEFEATED         ",
                "------------------------------------",
                f"Survivor ID: {final_state['survivor_id']}",
                f"Cause: {manifest.get('defeat_context', 'Unknown')}",
                f"Residue Preserved: {manifest.get('residue_carryover_profile', {}).get('preserved_residue', 0)}",
                f"Recovery Options: {[opt['type'] for opt in manifest.get('recovery_options', [])]}",
                "------------------------------------",
                "Initiating Recovery Protocol..."
            ]
            return "\n".join(screen_output)
        return ""

    def generate_visual_audit_overlay(self, audits):
        """Generates a simplified visual audit log/overlay."""
        overlay_lines = ["--- Visual Audit Overlay ---"]
        for audit in audits[-3:]: # Show last 3 audit events
            overlay_lines.append(f"[{audit['event']}] {json.dumps(audit['details'])}")
        overlay_lines.append("----------------------------")
        return "\n".join(overlay_lines)

    def get_full_presentation(self, game_state, audits, death_manifest=None):
        """Combines all visual elements into a single presentation."""
        presentation = []
        presentation.append(self.generate_hud_output(game_state))
        presentation.append("\n" + self.generate_map_layout(game_state))
        
        if game_state["has_died"] and death_manifest:
            presentation.append("\n" + self.generate_death_screen(game_state, death_manifest))
        
        # For CLI, let's just append the audit overlay at the end
        presentation.append("\n" + self.generate_visual_audit_overlay(audits))
        
        return "\n".join(presentation)

if __name__ == "__main__":
    # Internal test
    base_path = "engine/presentation/"
    vsm = VisualScaffoldManager(
        os.path.join(base_path, "visual_presentation_contract.json"),
        os.path.join(base_path, "hud_profile.json"),
        os.path.join(base_path, "placeholder_asset_manifest.json")
    )
    
    test_state = {
        "survivor_id": "TEST_SURVIVOR",
        "health": 75,
        "stamina": 60,
        "resources": {"FOOD": 5, "WATER": 3, "SCRAP": 10},
        "location": "Central Hub",
        "pressure": 45,
        "has_died": False,
        "play_session_id": "PS_XYZ"
    }
    
    test_audits = [
        {"timestamp": 123, "event": "PLAYER_INPUT", "details": {"action": "MOVE", "value": "NORTH"}},
        {"timestamp": 124, "event": "MOVEMENT", "details": {"profile": "move_standard", "location": "Moved North"}},
        {"timestamp": 125, "event": "COMBAT", "details": {"enemy": "enemy_generic", "feedback": "hit"}}
    ]
    
    # Test normal presentation
    print("--- Normal Game State ---")
    print(vsm.get_full_presentation(test_state, test_audits))
    
    # Test death presentation
    death_state = test_state.copy()
    death_state["health"] = 0
    death_state["has_died"] = True
    death_manifest = {
        "defeat_context": "Critical Wound",
        "residue_carryover_profile": {"preserved_residue": 0.8},
        "recovery_options": [{"type": "RECOVERY_RUN"}]
    } # Added missing brace
    print("\n--- Death Game State ---")
    print(vsm.get_full_presentation(death_state, test_audits, death_manifest))
