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

The importer first copies inputs into a private staging directory, verifies every
staged hash and bundle version before publishing any archive, refuses conflicting
destinations (including symlinks), and re-verifies the destination. Files are
published atomically without overwriting; a failed import removes only files
created by that run. Changes to the input folder cannot alter verified copies.
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

The build rejects missing or changed Intel inputs before asset cleanup/downloads.
It rebuilds `payloads.dmg` from those verified inputs on every asset-preparation
run, so an old image cannot silently omit imported drivers. Cached and freshly
downloaded official PatcherSupportPkg 2.0.3 images must match the pinned SHA256;
failed downloads are not retained as reusable images. Use `--reset-dmg-cache`
to redownload a rejected cache. When using individual build steps, always run
`--run-as-individual-steps --prepare-assets` after changing/importing inputs and
before `--prepare-application`; an application-only step is not asset preparation.

The build tool obtains official support assets and builds App/Pkg.
Do not run the installer to verify packaging. App builds without a Developer
ID are ad-hoc; Pkg is unsigned unless the builder independently supplies valid
signing inputs. No signing credentials are bundled.

## Public-checkout checks

These checks require no private compatibility archives or native macOS imports:

```sh
python3 -m pip install packaging requests
python3 tests/test_fork_safety.py
python3 -m compileall -q opencore_legacy_patcher ci_tooling tests tools
```

Run `python3 tests/test_intel_tahoe.py` separately after importing all five fixed
inputs; a missing archive is an error, not a silently skipped full integration test.

The active manual workflow checks source syntax, manifest structure and the
public-checkout safety regressions; it does
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

The Intel EFI profile is only defined for Sequoia/Darwin 24 and Tahoe/Darwin 25
build hosts. Each AirportItlwm variant is kernel-limited to that host's profile;
older or future hosts fail closed. Upstream application/nightly updates and
upstream AutoPkg seeding of installer media are disabled in this source fork.
