# Guarded Intel Tahoe profile

## Frozen inputs

- Official OCLP development base `8da38565fa1551a8e5ce8613ea835d04dd97e089`.
- OCLP-Mod donor/fork parent `63555b94610c74703a000058ac6876f65b92e638`.
- PatcherSupportPkg 2.0.3, official Universal-Binaries.dmg SHA256:
  `cf2a80deafe153ed4a9aa32c63463032e02718f32713e9b3f0a6e09f9a6ffbab`.
- KGP AirportItlwm-Tahoe formal 1.0.0 on Darwin 25 build hosts; Ventura 2.3.0
  on older build hosts. Matchers are the same 87 IDs; BE200 is not included.
- IntelBluetoothFirmware / IntelBTPatcher 2.5.0 fixed; BlueToolFixup 2.7.2 baseline.
- Exact archive versions and hashes: `payloads/Kexts/Intel/manifest.json`.

The selected profile depends on the host kernel. It does not infer another
machine's installation OS. KGP injection is gated to Darwin 25.0.0–25.99.99.

## Integration and guardrails

IntelWirelessCard is included in the modern-wireless candidate and networking
defaults. Official root-patch permission, SIP/AMFI/KDK checks and Tahoe patch
dictionaries are retained. Directly recognized Intel cards do not receive new
BCM device-property spoofing or enabled Broadcom NIC plugins.

EFI generation verifies all fixed payloads before extraction. The exact unused
legacy Broadcom NIC plugin can be cleaned only for a recognized Intel device
with its AirportItlwm entry enabled; arbitrary plugins/devices still fail.
Full compiled CLI output is restored to the working directory after asynchronous
payload preparation and must remain after process exit. App metadata/resource
edits occur before the final ad-hoc seal.

## Evidence and limits

Native x86_64 App/Pkg, AX210 IOKit detection, compiled CLI EFI generation,
13 regression tests and ad-hoc seal were verified on macOS 26.7.1. See
`VALIDATION.md`. The maintainer reports private-build testing, but no broad
hardware certification or public per-feature installation trace is claimed.

Neither AirDrop nor BE200 is advertised as working. This is the legacy wireless
framework profile, not a native-WCL / HE fork. An existing customized EFI needs
a reviewed merge rather than an automatic whole-directory replacement.

This source publication does not contain the new Intel ZIP archives; import
the exact separately acquired inputs using `tools/import_intel_payloads.py`.
Never substitute a similarly named new driver or silently change the manifest.
