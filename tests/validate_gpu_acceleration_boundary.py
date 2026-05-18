import os
import json

def run_gpu_boundary_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-004A",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    registry_path = os.path.join(project_root, "engine/core/acceleration_backend_registry.json")
    
    registry_data = {}

    def load_json_file(file_path, description):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            audit_results["checks"].append({"check": f"Load {description}", "status": "FAIL", "reason": str(e)})
            return None

    registry_data = load_json_file(registry_path, "acceleration_backend_registry.json")

    if not registry_data:
        return audit_results

    # Check 1: acceleration_backend_registry.json exists (handled by load_json_file)
    audit_results["checks"].append({"check": "acceleration_backend_registry.json exists", "status": "PASS"})

    # Check 2: CPU is declared as required backend
    cpu_required_check = {"check": "CPU is declared as required backend", "status": "PASS"}
    if registry_data.get("required_backend") != "cpu":
        cpu_required_check["status"] = "FAIL"
        cpu_required_check["reason"] = "'cpu' not declared as the required_backend."
    audit_results["checks"].append(cpu_required_check)

    # Check 3: GPU backends are optional only
    gpu_optional_check = {"check": "GPU backends are optional only", "status": "PASS"}
    if not isinstance(registry_data.get("optional_backends"), list):
        gpu_optional_check["status"] = "FAIL"
        gpu_optional_check["reason"] = "'optional_backends' is missing or not a list."
    else:
        # Ensure no optional backend is mistakenly marked as required
        if any(backend.get("backend_id") == registry_data.get("required_backend") for backend in registry_data["optional_backends"]):
             gpu_optional_check["status"] = "FAIL"
             gpu_optional_check["reason"] = "A GPU backend is listed as both optional and required."
        # This check primarily focuses on the conceptual separation and the `required_backend` field
        # The list itself being in "optional_backends" implies they are optional
    audit_results["checks"].append(gpu_optional_check)


    # Check 4: CUDA is not required
    cuda_not_required_check = {"check": "CUDA is not required", "status": "PASS"}
    if "cuda" not in registry_data.get("explicitly_not_required", []):
        cuda_not_required_check["status"] = "FAIL"
        cuda_not_required_check["reason"] = "'cuda' is not explicitly listed as not required."
    audit_results["checks"].append(cuda_not_required_check)

    # Check 5: WebGPU is listed for browser/web play path
    webgpu_listed_check = {"check": "WebGPU is listed for browser/web play path", "status": "PASS"}
    found_webgpu = False
    if isinstance(registry_data.get("optional_backends"), list):
        for backend in registry_data["optional_backends"]:
            if backend.get("backend_id") == "webgpu" and isinstance(backend.get("role"), list) and ("browser_rendering" in backend["role"] or "browser_compute_future" in backend["role"]):
                found_webgpu = True
                break
    if not found_webgpu:
        webgpu_listed_check["status"] = "FAIL"
        webgpu_listed_check["reason"] = "'webgpu' not found or not correctly configured for browser role."
    audit_results["checks"].append(webgpu_listed_check)

    # Check 6: CPU fallback policy is explicit
    cpu_fallback_explicit_check = {"check": "CPU fallback policy is explicit", "status": "PASS"}
    fallback_policy = registry_data.get("fallback_policy", {})
    if not (fallback_policy.get("cpu_required") is True and
            fallback_policy.get("gameplay_must_run_without_gpu_compute") is True and
            fallback_policy.get("gpu_may_accelerate_but_not_define_core_logic") is True):
        cpu_fallback_explicit_check["status"] = "FAIL"
        cpu_fallback_explicit_check["reason"] = "CPU fallback policy is not explicitly and correctly defined."
    audit_results["checks"].append(cpu_fallback_explicit_check)

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_004a_gpu_boundary_audit.json")

    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Audit results written to {audit_file_path}")
    return audit_results

if __name__ == "__main__":
    audit = run_gpu_boundary_audit()
    print(json.dumps(audit, indent=2))
