# Validation — 2026-10-14

## Recorded native-build evidence

Reference: MacBookAir7,2 with Broadwell / HD 6000 and Intel AX210, running
macOS 26.7.1 (25G241). Internal host aliases, home paths and raw machine logs
are intentionally not published.

- 13/13 regression tests passed on both the preparation host and the Mac.
  Unit tests stub native IOKit/NVRAM imports; a separate real IOKit probe
  detected Intel AX210 (8086:2725) and the modern-wireless patch candidate.
- Native x86_64 App and Pkg packaging completed successfully.
- Final App deep/strict ad-hoc seal verified; compiled `--help` and full
  `--build` exited successfully, with the generated EFI retained after exit.
- All 26 enabled kext references had their required files. KGP 1.0.0's Info
  and executable hashes matched the frozen official bundle; Bluetooth stayed
  2.5.0, BlueToolFixup 2.7.2, KGP kernel limits Darwin 25, DisableIoMapper=false.
- Expanded Pkg embedded the accepted App's Info.plist, executable and
  CodeResources; its ad-hoc seal verified too. App ZIP CRC and transfer hashes matched.
- GUI process and on-screen window metadata were observed, not screenshot-level QA.
- The official PatcherSupportPkg 2.0.3 DMG matched its release SHA256 and
  verified its internal CRCs during the documented read-only mounting process.

These records establish source → native App/Pkg → retained generated EFI.
They did not themselves install EFI/root patches or reboot the reference Mac.
The existing live KGP setup's networking results are not substituted for this
fork's complete installation acceptance.

## Maintainer's additional report

On 2026-10-14 the maintainer confirmed that the private application had already
been compiled and tested successfully. This report is retained as user-observed
testing, separately from the build evidence above. The message did not provide
a per-feature install/reboot trace, so this repository does not invent one or
claim a complete graphics/Bluetooth/sleep-wake/AirDrop certification matrix.

## Original publication snapshot

This source snapshot adds neutral branding, privacy-clean comments, current
documents, preserved notices and manual-only automation to the validated build
baseline. Core Intel detection, ID tables, root-patch selection, extraction,
security guards and fixed payload hashes remain unchanged. It has not been
recompiled as a renamed App; the private binaries are not published here.
Local publication checks and source hashes are delivered alongside the source
package, without publishing private build logs or identities.

## Post-publication source audit — 2026-10-14

The subsequent audit narrows Intel host eligibility to Darwin 24/25, bounds the
Sequoia injection kernel range, isolates upstream App/nightly/AutoPkg updates,
verifies support-image hashes, rebuilds local payload images after verification,
and makes the importer stage and publish validated copies with rollback.

These are **source changes after the native build above**; that App/Pkg was not
rebuilt, reinstalled or reboot-tested as part of this audit. GUI boundary tests
use a fake wx layer; they do not establish native visual or lifecycle QA.
The original 13 fixed-input tests and 25 added public-checkout tests are separate
suites. The latter use synthetic archives and mocked download/native boundaries;
they do not certify actual downloads, drivers or support DMG mounting on macOS.
The public checkout's 25 tests also run in the manual source-check workflow.
