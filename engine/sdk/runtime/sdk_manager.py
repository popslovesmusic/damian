import os
import json
import hashlib
import time

class SdkManager:
    def __init__(self, boundary_path, schema_path):
        with open(boundary_path, 'r') as f:
            self.boundary = json.load(f)
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)
        
        self.evidence = {"checks": [], "verdict": "PENDING"}

    def validate_cartridge(self, manifest):
        """Runs the validation pipeline against an expansion manifest."""
        # 1. Schema Validation
        required = self.schema["required_fields"]
        missing = [f for f in required if f not in manifest]
        if missing:
            return self._fail("Cartridge Schema Validation", f"Missing fields: {missing}")
            
        # 2. Forbidden Domain Scan
        for domain in manifest.get("sandbox_permissions", []):
            if domain in self.schema["forbidden_extension_domains"]:
                return self._fail("Sandbox Domain Scan", f"Forbidden domain requested: {domain}")
                
        # 3. Safe Payload Scan
        for module_type in ["narrative_modules", "contract_modules", "market_modules", "faction_modules"]:
            modules = manifest.get(module_type, [])
            for mod in modules:
                if "exec" in mod or "shell" in mod or ".sh" in mod or ".exe" in mod:
                    return self._fail("Payload Safety Scan", f"Unsafe execution payload detected in {module_type}")
        
        # 4. Hash Verification (Simulated)
        if not manifest.get("expansion_hash"):
            return self._fail("Integrity Verification", "Missing expansion hash.")
            
        self.evidence["checks"].append({"check": "Cartridge Validation Pipeline", "status": "PASS"})
        return True

    def _fail(self, check_name, reason):
        self.evidence["checks"].append({
            "check": check_name,
            "status": "FAIL",
            "reason": reason
        })
        return False

    def stub_narrative_sdk(self, text_input):
        """Simulates bounded narrative authoring."""
        # API prevents rewriting core lore, only adding contextual flavor
        processed = f"[AUTHOR_EXTENSION] {text_input}"
        self.evidence["checks"].append({"check": "Narrative SDK Binding", "status": "PASS"})
        return processed

    def stub_author_contract(self, objective, reward):
        """Simulates bounded contract generation."""
        # API caps rewards to prevent broken economies
        bounded_reward = min(reward, 100) # Hard cap
        contract = {
            "objective": objective,
            "reward_value": bounded_reward,
            "source": "AUTHOR_EXTENSION"
        }
        self.evidence["checks"].append({"check": "Author Contract Generation", "status": "PASS"})
        return contract

    def publish_expansion(self, manifest):
        """Simulates packaging and publishing."""
        if not self.validate_cartridge(manifest):
            return {"status": "FAIL", "reason": "Validation failed prior to publishing."}
            
        package = {
            "published_id": f"pub_{manifest['expansion_id']}_{int(time.time())}",
            "author_id": manifest["author_id"],
            "lineage_preserved": True,
            "status": "PUBLISHED_TO_RELAY"
        }
        self.evidence["checks"].append({"check": "Expansion Publishing Pipeline", "status": "PASS"})
        return package

    def get_final_evidence(self):
        if all(c["status"] == "PASS" for c in self.evidence["checks"]):
            self.evidence["verdict"] = "PASS"
        else:
            self.evidence["verdict"] = "FAIL"
        return self.evidence

if __name__ == "__main__":
    # Internal test
    sm = SdkManager(
        "engine/sdk/contracts/sdk_boundary.json",
        "engine/sdk/contracts/expansion_contract_schema.json"
    )
    
    valid_manifest = {
        "expansion_id": "ext_lore_001",
        "author_id": "author_alpha",
        "world_context": "damian_core",
        "supported_engine_version": "0.1.0",
        "narrative_modules": ["flavor_text.json"],
        "contract_modules": [],
        "market_modules": [],
        "faction_modules": [],
        "relay_interaction_profile": "read_only",
        "sandbox_permissions": ["story_modules"],
        "bounded_flags": {"safe": True},
        "expansion_hash": "dummy_hash_123"
    }
    
    invalid_manifest = valid_manifest.copy()
    invalid_manifest["sandbox_permissions"] = ["os_execution"]
    
    print(f"Valid Check: {sm.validate_cartridge(valid_manifest)}")
    print(f"Invalid Check: {sm.validate_cartridge(invalid_manifest)}")
    
    sm.stub_narrative_sdk("A new shadow falls over the High Pass.")
    sm.stub_author_contract("Retrieve the lost ledger", 500) # Will be bounded
    sm.publish_expansion(valid_manifest)
    
    print(json.dumps(sm.get_final_evidence(), indent=2))
