import os
import json
import shutil
import subprocess

def run_event_wave_validation():
    audit_results = {
        "patch_id": "STAGE-045",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/network/contracts/event_wave_boundary.json")
    contract_path = os.path.join(project_root, "engine/network/contracts/global_pressure_contract.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(contract_path):
        audit_results["checks"].append({"check": "Event wave boundary and contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Event wave boundary and contract defined", "status": "FAIL"})

    from engine.network.runtime.event_wave_manager import EventWaveManager
    wm = EventWaveManager(boundary_path, contract_path)

    # 2. Event Wave Generation
    wave = wm.generate_event_wave("RECLAMATION_WAVE")
    if "event_hash" in wave and wave["event_type"] == "RECLAMATION_WAVE":
        audit_results["checks"].append({"check": "Event wave generation stub produces bounded event", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Event wave generation stub produces bounded event", "status": "FAIL"})

    # 3. Pressure Propagation
    hubs = [{"relay_hub_id": "hub_test", "tower_attention_pressure": 30.0}]
    log = wm.propagate_pressure(wave, hubs)
    if len(log) == 1 and log[0]["status"] == "PROPAGATED_ASYNC":
        audit_results["checks"].append({"check": "Distributed pressure propagation remains asynchronous", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Distributed pressure propagation remains asynchronous", "status": "FAIL"})

    # 4. Probabilistic Forecast
    forecast = wm.generate_probabilistic_forecast(wave)
    if 0.5 <= forecast["confidence_level"] <= 1.0:
        audit_results["checks"].append({"check": "Pressure forecast stub avoids omniscience", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Pressure forecast stub avoids omniscience", "status": "FAIL"})

    # 5. Admin Terminal Integration
    # Store evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "event_wave_generation_result.json"), 'w') as f:
        json.dump(wave, f, indent=2)
    with open(os.path.join(output_dir, "global_pressure_forecast_result.json"), 'w') as f:
        json.dump(forecast, f, indent=2)
    with open(os.path.join(output_dir, "relay_pressure_propagation_result.json"), 'w') as f:
        json.dump(log, f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("event status")
    if "Active Event Wave Status" in res and "event_wave_id" in res:
        audit_results["checks"].append({"check": "Admin terminal reports event wave state safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports event wave state safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_045_event_wave_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Event Wave validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_event_wave_validation()
