import os
import json
import shutil
import subprocess

def run_live_audio_validation():
    audit_results = {
        "patch_id": "STAGE-040",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/network/contracts/audio_chat_boundary.json")
    session_contract_path = os.path.join(project_root, "engine/network/contracts/audio_session_contract.json")
    moderation_path = os.path.join(project_root, "engine/network/contracts/audio_moderation_boundary.json")

    # 1. Boundary & Contract Checks
    all_exist = all(os.path.exists(p) for p in [boundary_path, session_contract_path, moderation_path])
    if all_exist:
        audit_results["checks"].append({"check": "Live audio boundary and contracts defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Live audio boundary and contracts defined", "status": "FAIL"})

    # 2. Voice Session Stub
    from engine.network.runtime.voice_session_stub import VoiceSessionManager, AudioRouter
    vsm = VoiceSessionManager(session_contract_path)
    session = vsm.create_session("player_test", "private_party", ["player_test", "peer_test"])
    
    if "session_hash" in session and session["session_mode"] == "private_party":
        audit_results["checks"].append({"check": "Voice session stub produces bounded session", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Voice session stub produces bounded session", "status": "FAIL"})

    # 3. Audio Routing Isolation
    router = AudioRouter(moderation_path)
    route = router.route_audio(session, "player_test", "peer_test")
    if route["status"] == "ROUTED" and route.get("isolated") is True:
        audit_results["checks"].append({"check": "Audio routing stub isolates sessions safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Audio routing stub isolates sessions safely", "status": "FAIL"})

    # 4. Voice Presence Isolation
    if session["bounded_flags"].get("no_game_authority") is True:
        audit_results["checks"].append({"check": "Voice presence remains separate from game authority", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Voice presence remains separate from game authority", "status": "FAIL"})

    # 5. Admin Terminal Integration
    # Store session evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "voice_session_stub_result.json"), 'w') as f:
        json.dump(session, f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("audio status")
    if "Live Audio Session Status" in res and "session_id" in res:
        audit_results["checks"].append({"check": "Admin terminal reports session status", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports session status", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_040_live_audio_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Live Audio validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_live_audio_validation()
