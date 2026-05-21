import os
from engine.runtime.first_run_diagnostics import FirstRunDiagnostics
from engine.runtime.playable_slice_manager import PlayableSliceManager
from engine.runtime.walkable_prototype_manager import WalkablePrototypeManager

def main():
    base_path = "engine/"
    diagnostics = FirstRunDiagnostics(os.path.join(base_path, "runtime/first_run_contract.json"))
    results = diagnostics.run_checks()
    
    if not results["passed"]:
        print(f"Prototype launch failed: {results['errors']}")
        return

    # Setup PSM
    psm = PlayableSliceManager("engine/runtime/contracts/vertical_slice_contract.json")
    
    # Setup Prototype Manager
    wpm = WalkablePrototypeManager(
        os.path.join(base_path, "runtime/walkable_prototype_contract.json"),
        os.path.join(base_path, "runtime/player_controller_profile.json"),
        os.path.join(base_path, "runtime/prototype_launch_config.json"),
        psm
    )
    
    wpm.run_prototype()

if __name__ == "__main__":
    main()
