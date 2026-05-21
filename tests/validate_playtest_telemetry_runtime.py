import unittest
from engine.runtime.playtest_telemetry_manager import PlaytestTelemetryManager

class TestPlaytestTelemetry(unittest.TestCase):
    def setUp(self):
        self.ptm = PlaytestTelemetryManager(
            "engine/runtime/playtest_telemetry_contract.json",
            "engine/runtime/feel_metrics_profile.json",
            "engine/runtime/session_heatmap_rules.json",
            "engine/runtime/player_confusion_rules.json"
        )

    def test_telemetry_capture(self):
        # Capture event
        self.ptm.capture_event("TEST_EVENT", {"data": 1})
        self.assertEqual(len(self.ptm.telemetry_data), 1)
        self.assertEqual(self.ptm.telemetry_data[0]["event"], "TEST_EVENT")

if __name__ == "__main__":
    unittest.main()
