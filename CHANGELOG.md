# Fork changelog

## 2026-10-14 — post-publication source audit

- Block upstream App/nightly replacement and upstream AutoPkg inclusion on
  macOS installer media, including explicit update URLs and stale cached packages.
- Restrict the Intel profile to Darwin 24/25; bound both driver variants to their
  selected kernels and reject unsupported build hosts before payload access.
- Verify all Intel inputs before asset preparation, regenerate the payload DMG,
  verify cached/downloaded official support DMG hashes and discard partial files.
- Import immutable staged copies with no-overwrite publication and rollback;
  reject conflicting/symlink destinations and report missing inputs clearly.
- Add 25 public-checkout safety regressions to manual CI; retain the 13 full
  fixed-input tests and all upstream license text. No new native build is claimed.

## 2026-10-14 — source publication preparation

- Integrate the official Tahoe development baseline with the Intel detector
  adapted from OCLP-Mod; retain Mod's public ancestry and all source notices.
- Pin both 87-ID AirportItlwm profiles and Bluetooth 2.5.0; retain hash/version
  checks, exact Intel plugin cleanup guards, final App sealing and persistent CLI output.
- Replace stale prototype documents with current build evidence and clearly
  separated maintainer testing reports; remove internal machine aliases.
- Use neutral fork branding; no implied KGP/Dortania/laobamac endorsement.
- Archive upstream automatic release/Pages workflows as reference text;
  leave only an explicitly manual, non-publishing source-check workflow.
- Publish source/manifests and a guarded local payload importer, not the private
  App/Pkg or new compatibility binaries with unresolved source provenance.
