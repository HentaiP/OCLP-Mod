"""Fail closed when the known-working Intel compatibility set has changed."""

import hashlib
import json
import plistlib
import zipfile
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_pinned_payloads(folder: Path) -> None:
    manifest = json.loads((folder / "manifest.json").read_text())
    for item in manifest["payloads"]:
        archive = folder / item["archive"]
        if not archive.is_file():
            raise ValueError(f"Missing fixed Intel payload: {archive.name}. "
                             "Run tools/import_intel_payloads.py with the exact inputs before building.")
        if sha256_file(archive) != item["sha256"]:
            raise ValueError(f"Pinned Intel payload changed: {archive.name}")
        with zipfile.ZipFile(archive) as zf:
            info = plistlib.loads(zf.read(item["bundle"] + "/Contents/Info.plist"))
        if info["CFBundleVersion"] != item["version"]:
            raise ValueError(f"Pinned Intel payload version mismatch: {archive.name}")
