import json

class WalkablePrototypeManager:
    def __init__(self, contract_path, controller_path, launch_path, playable_slice_manager, diagnostics=None):
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        with open(controller_path, 'r') as f:
            self.controller_profile = json.load(f)
        with open(launch_path, 'r') as f:
            self.launch_config = json.load(f)
        self.psm = playable_slice_manager
        self.diagnostics = diagnostics

    def run_prototype(self):
        """Launches the prototype loop."""
        print("Launching Tower Walkable Prototype...")
        
        # Diagnostic check
        if self.diagnostics:
            results = self.diagnostics.run_checks()
            if not results["passed"]:
                print(f"Prototype diagnostics failed: {results['errors']}")
                return

        # Start interactive session
        while True:
            cmd = input("Action (MOVE <dir>|ATTACK <type>|PICKUP <type>|USE <type>|QUIT): ").split()
            if not cmd: continue
            action = cmd[0].upper()
            if action == "QUIT": break
            
            value = cmd[1] if len(cmd) > 1 else None
            
            # Map input to PSM
            result = self.psm.simulate_player_input(action, value)
            print(f"Result: {result}")
