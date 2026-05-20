import json
import os
import hashlib
import time

def create_image_artifact_stub():
    config_path = "os/kiosk/image_config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)

    image_dir = config["output"]["directory"]
    image_filename = config["output"]["filename"]
    image_path = os.path.join(image_dir, image_filename)
    
    os.makedirs(image_dir, exist_ok=True)

    # Create a dummy image file (stub)
    # We use a small file for the prototype to avoid disk bloat.
    with open(image_path, 'w') as f:
        f.write(f"DAMIAN TOWER OS BOOTABLE IMAGE STUB\nID: {config['image_id']}\nTIMESTAMP: {time.time()}\n")

    print(f"Image artifact stub created at {image_path}")

    # Calculate Hash
    sha256_hash = hashlib.sha256()
    with open(image_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    image_hash = sha256_hash.hexdigest()

    # Create Manifest
    manifest = {
        "image_id": config["image_id"],
        "filename": image_filename,
        "hash_sha256": image_hash,
        "format": config["format"],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "partitions": config["labels"]
    }

    manifest_path = os.path.join(image_dir, "tower_image_manifest.json")
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"Image manifest created at {manifest_path}")
    return manifest

if __name__ == "__main__":
    create_image_artifact_stub()
