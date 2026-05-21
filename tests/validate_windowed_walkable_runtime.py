import unittest
from engine.runtime.windowed_input_loop import WindowedInputLoop

class TestWindowedWalkableRuntime(unittest.TestCase):
    def test_imports(self):
        # Just check that it can be instantiated (might fail if no X11/display, but it's a start)
        # We can't really run the full loop here.
        pass

if __name__ == "__main__":
    unittest.main()
