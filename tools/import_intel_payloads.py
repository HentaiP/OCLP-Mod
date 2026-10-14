#!/usr/bin/env python3
"""Import separately obtained fixed archives; never download, upgrade or install."""
import argparse
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-dir", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    destination = root / "payloads/Kexts/Intel"
    source = args.from_dir.expanduser().resolve()
    manifest = json.loads((destination / "manifest.json").read_text())
    spec = importlib.util.spec_from_file_location(
        "fixed_payload_verifier", root / "opencore_legacy_patcher/support/intel_wifi_payloads.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # The verifier reads a manifest next to archives; stage only the manifest
    # in an owned temporary sibling when the input folder has no exact copy.
    import tempfile
    with tempfile.TemporaryDirectory(prefix="oclp-payload-check-", dir=destination) as temporary:
        stage = Path(temporary)
        shutil.copy2(destination / "manifest.json", stage / "manifest.json")
        for item in manifest["payloads"]:
            path = source / item["archive"]
            if not path.is_file():
                raise SystemExit("Missing input: " + item["archive"])
            target = destination / item["archive"]
            if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != item["sha256"]:
                raise SystemExit("Refusing to overwrite conflicting destination: " + item["archive"])
            (stage / item["archive"]).symlink_to(path)
        module.verify_pinned_payloads(stage)
        for item in manifest["payloads"]:
            target = destination / item["archive"]
            if not target.exists():
                shutil.copy2(source / item["archive"], target)
        module.verify_pinned_payloads(destination)
    print("Verified " + str(len(manifest["payloads"])) + " fixed archives; no system changes made.")


if __name__ == "__main__":
    main()
