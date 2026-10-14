#!/usr/bin/env python3
"""Import separately obtained fixed archives; never download, upgrade or install."""
import argparse
import importlib.util
import json
import os
import shutil
import tempfile
from pathlib import Path


def import_payloads(source: Path, destination: Path) -> int:
    """Validate a private copy, then publish complete files without overwriting."""
    root = Path(__file__).resolve().parents[1]
    source = source.expanduser().resolve()
    manifest = json.loads((destination / "manifest.json").read_text())
    spec = importlib.util.spec_from_file_location(
        "fixed_payload_verifier", root / "opencore_legacy_patcher/support/intel_wifi_payloads.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    names = [item["archive"] for item in manifest["payloads"]]
    if not names or len(names) != len(set(names)) or any(
        Path(name).name != name or name in (".", "..") for name in names
    ):
        raise ValueError("Manifest must contain unique, local archive filenames")
    # Symlinks to mutable inputs would validate one set of bytes and later copy
    # another. Copy everything first and verify exactly what will be installed.
    with tempfile.TemporaryDirectory(prefix="oclp-payload-check-", dir=destination) as temporary:
        stage = Path(temporary)
        shutil.copy2(destination / "manifest.json", stage / "manifest.json")
        for item in manifest["payloads"]:
            path = source / item["archive"]
            if not path.is_file():
                raise ValueError("Missing input: " + item["archive"])
            target = destination / item["archive"]
            if target.is_symlink() or (target.exists() and (
                not target.is_file() or module.sha256_file(target) != item["sha256"]
            )):
                raise ValueError("Refusing to overwrite conflicting destination: " + item["archive"])
            shutil.copy2(path, stage / item["archive"])
        module.verify_pinned_payloads(stage)
        created = []
        try:
            for item in manifest["payloads"]:
                target = destination / item["archive"]
                try:
                    # Stage and destination share a filesystem. link() makes a
                    # complete file visible atomically and never overwrites one.
                    os.link(stage / item["archive"], target)
                    created.append((target, target.stat().st_ino))
                except FileExistsError:
                    if target.is_symlink() or not target.is_file() or module.sha256_file(target) != item["sha256"]:
                        raise ValueError("Conflicting destination appeared during import: " + item["archive"])
            module.verify_pinned_payloads(destination)
        except Exception:
            for target, inode in created:
                if target.exists() and not target.is_symlink() and target.stat().st_ino == inode:
                    target.unlink()
            raise
    return len(manifest["payloads"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-dir", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        count = import_payloads(args.from_dir, root / "payloads/Kexts/Intel")
    except (OSError, ValueError) as exc:
        parser.exit(1, str(exc) + "\n")
    print(f"Verified {count} fixed archives; no system changes made.")


if __name__ == "__main__":
    main()
