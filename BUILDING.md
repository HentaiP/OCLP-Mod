# Build from source

## Environment

The recorded build used Intel x86_64, macOS 26.7.1 (25G241), Python 3.11.0
and Xcode clang 17.0.0. `requirements-x86_64-20261014.lock.txt` preserves that
environment's package versions; it is not an older-macOS or universal2 guarantee.
The upstream universal2 default remains available, but only x86_64 is evidenced here.

## Compatibility inputs

Separately obtain the five archives named by `payloads/Kexts/Intel/manifest.json`.
The archives are **not distributed in this source fork**. The Bluetooth 2.5.0
builds in the validation baseline do not have an identified official release tag
or exact corresponding-source revision; do not assume official v2.4.0 is interchangeable.
The other exact source identities and notices are in `THIRD_PARTY_NOTICES.md`.

If the files are available in a local input folder:

```sh
python3 tools/import_intel_payloads.py --from-dir /path/to/exact-input-archives
```

The importer verifies every input hash and bundle version before copying any
archive, refuses conflicting destinations, and re-verifies the destination.
It does not install drivers, modify EFI, download unknown archives, update
Bluetooth versions or disable payload checks. Local inputs remain Git-ignored.

## Native build

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-x86_64-20261014.lock.txt
python3 tests/test_intel_tahoe.py
OCLP_BUILD_ARCH=x86_64 python3 Build-Project.command
```

The upstream build tool obtains official support assets and builds App/Pkg.
Do not run the installer to verify packaging. App builds without a Developer
ID are ad-hoc; Pkg is unsigned unless the builder independently supplies valid
signing inputs. No signing credentials are bundled.

The active manual workflow checks source syntax and manifest structure; it does
not pretend that a source-only checkout contains the private compatibility
inputs needed for a native App build. The previous native-build workflow is
preserved as reference text under `docs/upstream/workflows/`.
No hosted native build, old macOS runtime or Apple Silicon execution has been
validated for this fork. Normal source pushes do not trigger builds, GitHub
Pages or releases.

## Check the finished build

Use `codesign --verify --deep --strict` on the final App, run the compiled
`--help` and complete `--build` from a dedicated writable directory, and confirm
that the generated EFI is still there after process exit. Check all enabled
kext references, manifest identity and kernel limits. Preserve existing
picker/theme/multiboot settings if later merging into a live configuration.
