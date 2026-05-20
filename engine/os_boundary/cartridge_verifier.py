import os
import json
import hashlib

class CartridgeVerifier:
    def __init__(self, boundary_contract_path, manifest_contract_path):
        with open(boundary_contract_path, 'r') as f:
            self.boundary = json.load(f)
        with open(manifest_contract_path, 'r') as f:
            self.manifest_contract = json.load(f)
        
        self.evidence = {
            "checks": [],
            "verdict": "PENDING"
        }

    def verify_manifest_schema(self, manifest):
        """Checks if required fields are present and forbidden fields are absent."""
        required = self.manifest_contract["required_fields"]
        forbidden = self.manifest_contract["forbidden_fields"]
        
        present_fields = manifest.keys()
        missing = [f for f in required if f not in present_fields]
        found_forbidden = [f for f in forbidden if f in present_fields]
        
        status = "PASS" if not missing and not found_forbidden else "FAIL"
        reason = ""
        if missing:
            reason += f"Missing fields: {missing}. "
        if found_forbidden:
            reason += f"Forbidden fields found: {found_forbidden}."
            
        self.evidence["checks"].append({
            "check": "Manifest Schema Audit",
            "status": status,
            "reason": reason
        })
        return status == "PASS"

    def safety_scan(self, manifest):
        """Scans declared files for path traversals and unsafe payloads."""
        declared_files = manifest.get("declared_files", [])
        status = "PASS"
        reason = ""
        
        for file_path in declared_files:
            # 1. Path Traversal check
            if ".." in file_path or file_path.startswith("/"):
                status = "FAIL"
                reason = f"Path traversal detected: {file_path}"
                break
            
            # 2. Executable payload check (basic extension check for prototype)
            unsafe_extensions = [".sh", ".py", ".exe", ".bin", ".so"]
            if any(file_path.endswith(ext) for ext in unsafe_extensions):
                 # Note: launcher itself is .py, but content packs shouldn't contain scripts.
                 status = "FAIL"
                 reason = f"Unsafe executable payload declared: {file_path}"
                 break

        self.evidence["checks"].append({
            "check": "Content Safety Scan",
            "status": status,
            "reason": reason
        })
        return status == "PASS"

    def verify_hashes(self, base_dir, manifest):
        """Verifies SHA256 hashes of declared files against the manifest."""
        hash_manifest = manifest.get("sha256_manifest", {})
        status = "PASS"
        reason = ""
        
        for file_path, expected_hash in hash_manifest.items():
            full_path = os.path.join(base_dir, file_path)
            if not os.path.exists(full_path):
                status = "FAIL"
                reason = f"Declared file missing: {file_path}"
                break
            
            sha256_hash = hashlib.sha256()
            with open(full_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            if sha256_hash.hexdigest() != expected_hash:
                status = "FAIL"
                reason = f"Hash mismatch for {file_path}"
                break

        self.evidence["checks"].append({
            "check": "Hash Verification",
            "status": status,
            "reason": reason
        })
        return status == "PASS"

    def generate_load_plan(self, manifest):
        """Generates a read-only load plan for the cartridge."""
        plan = {
            "content_pack_id": manifest["content_pack_id"],
            "mount_mode": "read_only",
            "asset_dirs": manifest["allowed_asset_dirs"],
            "entry_point": manifest["entry_content"]
        }
        self.evidence["load_plan"] = plan
        return plan

    def get_final_evidence(self):
        if all(c["status"] == "PASS" for c in self.evidence["checks"]):
            self.evidence["verdict"] = "PASS"
        else:
            self.evidence["verdict"] = "FAIL"
        return self.evidence

if __name__ == "__main__":
    # Test stub with Damian manifest
    dummy_manifest = {
        "content_pack_id": "damian",
        "display_name": "Damian: What Survives the Tower",
        "version": "1.0.0",
        "engine_min_version": "0.0.1",
        "pack_type": "tower_world",
        "world_identity": "damian_core",
        "entry_content": "floors/floor_1.json",
        "allowed_asset_dirs": ["enemies", "floors", "items", "story"],
        "declared_files": ["content_pack.json", "domain_binding.json"],
        "sha256_manifest": {
             "content_pack.json": "fake_hash",
             "domain_binding.json": "fake_hash"
        },
        "bounded_flags": {"immutable": True}
    }
    
    verifier = CartridgeVerifier(
        "engine/os_boundary/contracts/content_pack_cartridge_boundary.json",
        "engine/os_boundary/contracts/content_pack_manifest_contract.json"
    )
    
    verifier.verify_manifest_schema(dummy_manifest)
    verifier.safety_scan(dummy_manifest)
    # verify_hashes would fail with fake_hash
    
    print(json.dumps(verifier.get_final_evidence(), indent=2))
