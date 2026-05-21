from engine.runtime.playable_slice_manager import PlayableSliceManager
from engine.runtime.windowed_input_loop import WindowedInputLoop

def main():
    # Setup PSM
    psm = PlayableSliceManager("engine/runtime/contracts/vertical_slice_contract.json")
    
    # Run the interactive loop
    loop = WindowedInputLoop(psm)
    loop.run()

if __name__ == "__main__":
    main()
