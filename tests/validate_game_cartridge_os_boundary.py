import os
import json

def run_game_cartridge_os_boundary_audit():
    audit_results = {
        "patch_id": "STAGE-021",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    registry_path = os.path.join(project_root, "engine/os_boundary/contracts/game_cartridge_os_boundary.json")

    def load_json_file(file_path, description):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            audit_results["checks"].append({"check": f"Load {description}", "status": "FAIL", "reason": str(e)})
            return None

    registry_data = load_json_file(registry_path, "game_cartridge_os_boundary.json")
    if not registry_data:
        return audit_results

    audit_results["checks"].append({"check": "game_cartridge_os_boundary.json exists", "status": "PASS"})

    # TOWER-ENGINE-179: Define Immutable Runtime Core Layout
    immutable_core_check = {"check": "TOWER_OS partition is defined as read-only and immutable", "status": "PASS"}
    tower_os = registry_data.get("partitions", {}).get("TOWER_OS", {})
    if tower_os.get("mode") != "read_only_live_system" or not tower_os.get("immutable"):
        immutable_core_check["status"] = "FAIL"
        immutable_core_check["reason"] = "TOWER_OS must be read_only_live_system and immutable."
    audit_results["checks"].append(immutable_core_check)

    # TOWER-ENGINE-180: Define Persistent Tower Data Partition
    persistent_data_check = {"check": "TOWER_DATA partition is defined as read-write and persistent", "status": "PASS"}
    tower_data = registry_data.get("partitions", {}).get("TOWER_DATA", {})
    if tower_data.get("mode") != "read_write_persistent" or tower_data.get("immutable"):
        persistent_data_check["status"] = "FAIL"
        persistent_data_check["reason"] = "TOWER_DATA must be read_write_persistent and mutable."
    audit_results["checks"].append(persistent_data_check)

    # TOWER-ENGINE-181: Define Kiosk Boot and Game Launcher Boundary
    kiosk_boot_check = {"check": "Kiosk boot rules prohibit bootloader and kernel mods", "status": "PASS"}
    kiosk_boot = registry_data.get("kiosk_boot", {})
    if kiosk_boot.get("bootloader_modification_allowed") is True or kiosk_boot.get("kernel_customization_allowed") is True:
        kiosk_boot_check["status"] = "FAIL"
        kiosk_boot_check["reason"] = "Bootloader and kernel modifications are not allowed yet."
    audit_results["checks"].append(kiosk_boot_check)

    # TOWER-ENGINE-182: Define Restricted Admin Terminal Boundary
    restricted_terminal_check = {"check": "Admin terminal is restricted and no remote admin", "status": "PASS"}
    admin_term = registry_data.get("admin_terminal", {})
    if not admin_term.get("restricted") or admin_term.get("remote_admin_runtime_allowed") is True or admin_term.get("destructive_disk_partitioning_allowed") is True:
        restricted_terminal_check["status"] = "FAIL"
        restricted_terminal_check["reason"] = "Admin terminal must be restricted, no remote admin, no destructive partitioning."
    audit_results["checks"].append(restricted_terminal_check)

    # TOWER-ENGINE-183: Define Content Pack Cartridge Boundary
    content_pack_check = {"check": "Content packs are verifiable and location separated", "status": "PASS"}
    content_packs = registry_data.get("content_packs", {})
    if not content_packs.get("verifiable") or content_packs.get("default_location") != "TOWER_OS" or content_packs.get("override_location") != "TOWER_DATA":
        content_pack_check["status"] = "FAIL"
        content_pack_check["reason"] = "Content packs must be verifiable, defaults in OS, overrides in DATA."
    audit_results["checks"].append(content_pack_check)

    # TOWER-ENGINE-184: Define Live USB Build Artifact Boundary
    build_artifact_check = {"check": "Live USB artifact constraints are respected", "status": "PASS"}
    build_artifact = registry_data.get("build_artifact", {})
    if build_artifact.get("iso_build_automation_implemented") is True or build_artifact.get("driver_bundle_creation_implemented") is True:
        build_artifact_check["status"] = "FAIL"
        build_artifact_check["reason"] = "ISO build automation and driver bundles are not implemented yet."
    audit_results["checks"].append(build_artifact_check)

    # TOWER-ENGINE-185: Define Kiosk OS Security and Recovery Boundary
    security_recovery_check = {"check": "Security and recovery rules are respected", "status": "PASS"}
    security = registry_data.get("security_recovery", {})
    if security.get("network_update_runtime_allowed") is True or security.get("real_multiplayer_server_allowed") is True:
        security_recovery_check["status"] = "FAIL"
        security_recovery_check["reason"] = "Network updates and real multiplayer are not allowed yet."
    audit_results["checks"].append(security_recovery_check)

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "stage_021_game_cartridge_os_boundary_audit.json")

    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Audit results written to {audit_file_path}")
    return audit_results

if __name__ == "__main__":
    audit = run_game_cartridge_os_boundary_audit()
    print(json.dumps(audit, indent=2))
