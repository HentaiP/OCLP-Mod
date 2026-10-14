"""Fail closed when the known-working Intel compatibility set has changed."""

import hashlib
import json
import plistlib
import zipfile
from pathlib import Path


def verify_pinned_payloads(folder: Path) -> None:
    manifest = json.loads((folder / "manifest.json").read_text())
    for item in manifest["payloads"]:
        archive = folder / item["archive"]
        if hashlib.sha256(archive.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"Pinned Intel payload changed: {archive.name}")
        with zipfile.ZipFile(archive) as zf:
            info = plistlib.loads(zf.read(item["bundle"] + "/Contents/Info.plist"))
        if info["CFBundleVersion"] != item["version"]:
            raise ValueError(f"Pinned Intel payload version mismatch: {archive.name}")
