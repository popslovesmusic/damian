import os
from engine.runtime.playable_slice_manager import PlayableSliceManager
from engine.runtime.walkable_prototype_manager import WalkablePrototypeManager

def main():
    base_path = "engine/"
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
