import json
import os

class IsometricRenderManager:
    def __init__(self, contract_path, tile_rules_path, lighting_path, fog_path, manifest_path, animation_manager=None, lighting_manager=None, asset_selection_manager=None, performance_manager=None):
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        with open(tile_rules_path, 'r') as f:
            self.tile_rules = json.load(f)
        with open(lighting_path, 'r') as f:
            self.lighting_profile = json.load(f)
        with open(fog_path, 'r') as f:
            self.fog_rules = json.load(f)
        with open(manifest_path, 'r') as f:
            self.manifest = json.load(f)
        self.animation_manager = animation_manager
        self.lighting_manager = lighting_manager
        self.asset_selection_manager = asset_selection_manager
        self.performance_manager = performance_manager

    def render_room(self, room_data, pressure, player_pos, feedback_layers=None, animation_state=None, lighting_params=None):
        """Generates a text-based isometric view of a room."""
        brightness = lighting_params.get("brightness", 0.8) if lighting_params else 0.8
        
        # This is a simplified isometric layout for the prototype
        render_output = [
            f"--- Isometric View | Pressure: {pressure} | Light: {brightness} ---",
            f"Room: {room_data.get('room_id')}",
            r"   / \   ",
            r"  /   \  ",
            " |     | ",
            r"  \   /  ",
            r"   \ /   "
        ]
        
        # Simplified hazard overlay
        if room_data.get("hazards"):
            render_output.append(f"Effects: {len(room_data['hazards'])} active hazards")
            if self.performance_manager:
                self.performance_manager.report_usage("effects", len(room_data['hazards']))
            
        if feedback_layers:
            for layer, effect in feedback_layers.items():
                render_output.append(f"Visual Feedback: {layer} -> {effect}")
                if self.performance_manager:
                    self.performance_manager.report_usage("effects", 1)

        if animation_state:
            # Check asset approval
            if self.asset_selection_manager and not self.asset_selection_manager.is_asset_approved("enemies", animation_state):
                render_output.append(f"Animations: [UNAPPROVED] {animation_state}")
                self.asset_selection_manager.log_rejection("enemies", animation_state, "unapproved asset")
            else:
                render_output.append(f"Animations: {animation_state}")
            if self.performance_manager:
                self.performance_manager.report_usage("entities", 1)
        
        return "\n".join(render_output)

    def render_overlay(self, pressure, feedback_layers=None, lighting_params=None):
        """Generates fog/atmosphere overlay."""
        fog_density = lighting_params.get("fog_density", 0.0) if lighting_params else 0.0
        overlay = "[ Fog: Base | Clear ]"
        if fog_density > 0.4 or (feedback_layers and "pressure" in feedback_layers):
            overlay = "[ Fog: Dense | Occlusion Active ]"
            
        return overlay

    def get_full_isometric_frame(self, game_state, feedback_layers=None, animation_state=None):
        """Combines all isometric elements."""
        room = game_state.get("floor", {}).get("rooms", [{}])[0] # Get first room for prototype
        pressure = game_state.get("pressure", 0)
        
        lighting_params = self.lighting_manager.get_render_parameters(game_state) if self.lighting_manager else {}
        
        frame = []
        frame.append(self.render_room(room, pressure, (0,0), feedback_layers, animation_state, lighting_params))
        frame.append(self.render_overlay(pressure, feedback_layers, lighting_params))
        
        return "\n".join(frame)
