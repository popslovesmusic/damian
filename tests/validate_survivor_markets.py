import os
import json
import shutil
import subprocess

def run_market_validation():
    audit_results = {
        "patch_id": "STAGE-046",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/domain/contracts/market_boundary.json")
    contract_path = os.path.join(project_root, "engine/domain/contracts/resource_exchange_contract.json")
    anti_monopoly_path = os.path.join(project_root, "engine/domain/contracts/anti_monopoly_boundary.json")

    # 1. Boundary & Contract Checks
    if all(os.path.exists(p) for p in [boundary_path, contract_path, anti_monopoly_path]):
        audit_results["checks"].append({"check": "Market boundary and contracts defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Market boundary and contracts defined", "status": "FAIL"})

    from engine.domain.market_manager import MarketManager
    mm = MarketManager(boundary_path, contract_path, anti_monopoly_path)

    # 2. Market Listing
    resource = {"type": "residue", "weight": 50}
    exchange = {"type": "token", "value": 10}
    listing = mm.create_listing("survivor_test", "residue_artifact", resource, exchange)
    if "listing_hash" in listing and listing["seller_survivor_id"] == "survivor_test":
        audit_results["checks"].append({"check": "Market listing stub produces bounded listings", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Market listing stub produces bounded listings", "status": "FAIL"})

    # 3. Market Instability
    initial_mod = listing["visibility_pressure_modifier"]
    mm.resolve_market_instability([listing], 60.0) # High pressure
    if listing["visibility_pressure_modifier"] > initial_mod:
        audit_results["checks"].append({"check": "Market instability introduces procedural pressure", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Market instability introduces procedural pressure", "status": "FAIL"})

    # 4. Residue Trade Lineage
    if mm.validate_residue_trade(listing):
        audit_results["checks"].append({"check": "Residue artifact trade preserves lineage", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Residue artifact trade preserves lineage", "status": "FAIL"})

    # 5. Admin Terminal Integration
    # Store evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "market_listing_result.json"), 'w') as f:
        json.dump(listing, f, indent=2)
    with open(os.path.join(output_dir, "market_instability_result.json"), 'w') as f:
        json.dump(mm.get_final_evidence(), f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("market status")
    if "Survivor Market Status" in res and "listing_id" in res:
        audit_results["checks"].append({"check": "Admin terminal reports market state safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports market state safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_046_survivor_market_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Market validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_market_validation()
