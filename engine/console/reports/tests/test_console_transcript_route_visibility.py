import pytest
from engine.console.reports import console_transcript_reporter

def test_console_transcript_route_visibility():
    commands = ["traverse", "status"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, 
        transcript_id="route_visibility_validation"
    )
    
    assert transcript["ok"]
    assert "route_selections_observed" in transcript
    assert transcript["route_selections_observed"] > 0
    assert "route_hazard_visibility_summaries" in transcript
    assert len(transcript["route_hazard_visibility_summaries"]) > 0
    assert "average_information_accuracy_observed" in transcript
    assert "visibility_bands_observed" in transcript
