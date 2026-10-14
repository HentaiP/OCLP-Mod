# OCLP-Mod — Intel Tahoe fork

**Powered by HentaiP feat. Maha**

A source-available, non-commercial OCLP-Mod fork integrating the official
Tahoe development baseline with guarded Intel Wi-Fi support. This is an
independent fork, not an official release or an endorsement by any upstream author.

[繁體中文](README.zh-TW.md) · [Build](BUILDING.md) · [Validation](VALIDATION.md)
· [Intel profile](INTEL_TAHOE.md) · [Licensing](THIRD_PARTY_NOTICES.md)

**This product includes software developed by Dortania and OpenCore Legacy Patcher contributors.**
**This product includes software developed by Dortania and OCLP contributors.**

This work is derived from laobamac/OCLP-Mod (https://github.com/laobamac/OCLP-Mod),
governed by the OCLP-Mod Private Open Source License.
Commercial derivatives require written authorization from Wang Xiaoci.

## Why this fork

OCLP-Mod's upstream README announces archival from June 13, 2026. This branch
retains that project's public Git ancestry and preserves its license notices,
while integrating a newer official Tahoe base. It is not a complete continuation
of Mod's Chinese interface or SimpleHacAPI services.

## Integration

- Official OCLP development base: `8da38565fa1551a8e5ce8613ea835d04dd97e089`.
  The inherited `3.0.0` version identifies development source, not a stable release.
- OCLP-Mod donor / fork parent: `63555b94610c74703a000058ac6876f65b92e638`.
- Official PatcherSupportPkg **2.0.3** and its original download origin retained.
- Intel recognition restricted to **87 PCI IDs** from the pinned driver matchers;
  detection is eligibility, not a guarantee for every listed card. BE200 is excluded.
- Darwin 25 build hosts select **KGP AirportItlwm-Tahoe 1.0.0**, gated to Darwin 25;
  older build hosts select **AirportItlwm Ventura 2.3.0**.
- **IntelBluetoothFirmware / IntelBTPatcher 2.5.0** remain fixed;
  BlueToolFixup **2.7.2** is the tested baseline.
- Payload hash/version checks fail closed. Existing root-patch security checks,
  unknown-plugin rejection and official graphics/USB patch dictionaries remain.
- Final ad-hoc sealing and persistent compiled-CLI EFI output fixes are retained.

The driver selection follows the **build host kernel**, not an independently
detected external destination OS. Review the generated profile before installation.
This legacy wireless profile is not the newer native-WCL / HE Wi-Fi 6 driver.
AirDrop and BE200 are not advertised as working.

## Status

Native Intel App/Pkg build, real AX210 detection and retained compiled-CLI EFI
generation were verified on macOS 26.7.1. Thirteen regression tests passed on
the preparation host and the Mac. The maintainer also reports testing the
private build successfully; see [the exact evidence boundaries](VALIDATION.md).

This repository publishes **source and pinned manifests**, not the private App,
installer or new Intel compatibility archives. Import separately obtained,
exact-matching payloads with `tools/import_intel_payloads.py`; it never updates
versions or bypasses hashes. Exact source provenance for the existing Bluetooth
2.5.0 binaries is not yet established, so those binaries are not redistributed here.

Inherited updater/support URLs still refer to the original OCLP project;
this source snapshot does not provide its own binary update channel.

Only an explicitly manual, non-publishing source-check workflow is active. Native
builds use the local instructions and separately acquired inputs. No CI run,
live EFI installation, root patch or reboot is initiated by this source package.

## Credits and terms

Dortania and all OpenCore Legacy Patcher contributors; laobamac/OCLP-Mod for
Intel detection; kgp-macPro for AirportItlwm-Tahoe; OpenIntelWireless for Intel
Wi-Fi/Bluetooth drivers; Acidanthera for OpenCore and BrcmPatchRAM/BlueToolFixup.
Full inherited credits are preserved in [the upstream README](docs/upstream/README-Dortania.md).

Retain [LICENSE.txt](LICENSE.txt), [LICENSE.md](LICENSE.md), the Mod copyright
notice in [licenses/](licenses/), and all third-party notices. Mod's additional
terms distinguish direct GitHub forks from independent derivative publication
and restrict commercial distribution. The combined project is **not presented
as an unrestricted BSD/MIT or OSI-approved distribution**. See the original
terms before publishing a standalone package or commercial derivative.
