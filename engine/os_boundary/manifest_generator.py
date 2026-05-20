import os
import json
import hashlib

def generate_cartridge_manifest(content_dir, pack_id, display_name):
    manifest = {
        "content_pack_id": pack_id,
        "display_name": display_name,
        "version": "1.0.0",
        "engine_min_version": "0.0.1",
        "pack_type": "tower_world",
        "world_identity": f"{pack_id}_core",
        "entry_content": "floors/floor_1.json",
        "allowed_asset_dirs": ["enemies", "floors", "items", "story"],
        "declared_files": [],
        "sha256_manifest": {},
        "bounded_flags": {"immutable": True}
    }

    for root, dirs, files in os.walk(content_dir):
        for file in files:
            if file == "cartridge_manifest.json":
                continue
            
            rel_path = os.path.relpath(os.path.join(root, file), content_dir).replace("\\", "/")
            manifest["declared_files"].append(rel_path)
            
            sha256_hash = hashlib.sha256()
            with open(os.path.join(root, file), "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            manifest["sha256_manifest"][rel_path] = sha256_hash.hexdigest()

    output_path = os.path.join(content_dir, "cartridge_manifest.json")
    with open(output_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"Generated manifest for {pack_id} at {output_path}")

if __name__ == "__main__":
    generate_cartridge_manifest("content/damian", "damian", "Damian: What Survives the Tower")
    generate_cartridge_manifest("content/jacobs_bane", "jacobs_bane", "Jacob's Bane")
