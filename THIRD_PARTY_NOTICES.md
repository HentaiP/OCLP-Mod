# Copyright, licensing and frozen third-party inputs

## Patcher source

This product includes software developed by Dortania and OpenCore Legacy Patcher contributors.
This product includes software developed by Dortania and OCLP contributors.

- Official OCLP's `LICENSE.txt` contains **four** numbered conditions, including
  an advertising acknowledgement; it must not be summarized as plain BSD-3.
- OCLP-Mod's original `LICENSE.md` and `licenses/OCLP-Mod-LICENSE.txt` are
  preserved verbatim. `LICENSE.md` includes MIT text followed by a private
  license that says its overlapping restrictions take priority. It expressly
  excludes direct GitHub-fork repositories from its derivative-work definition,
  permits modification of such forks, and restricts commercial distribution.
  It separately restricts independent derivative publication.
- This snapshot is prepared for a direct **GitHub fork of laobamac/OCLP-Mod**,
  not a fresh independent repository or a claim of unrestricted relicensing.
  A local archive, Git clone or Git bundle does not by itself create GitHub's
  fork relationship. The separate package is a preparation/handoff artifact.
- No authorization letter, author endorsement or right to independently
  publish a compiled derivative is claimed. Retain these notices when forking.

This work is derived from laobamac/OCLP-Mod (https://github.com/laobamac/OCLP-Mod),
governed by the OCLP-Mod Private Open Source License.
Commercial derivatives require written authorization from Wang Xiaoci.

## New Intel compatibility inputs

Exact bytes and versions are fixed in `payloads/Kexts/Intel/manifest.json`.
The new Intel ZIP archives are not included in the Git-tracked public tree.
Hashes identify local inputs; they do not grant permission or establish source identity.

- **AirportItlwm Ventura 2.3.0**: OpenIntelWireless/itlwm,
  tag `v2.3.0`, commit `4ac4c79bc7e34f8764038fc382630a29eb46213d`.
  GPL driver and separately licensed Intel wireless firmware;
  https://github.com/OpenIntelWireless/itlwm/tree/v2.3.0 .
- **KGP AirportItlwm-Tahoe 1.0.0**: kgp-macPro/AirportItlwm-Tahoe,
  tag `v1.0.0`, commit `20daea29bc8474e77f42fc7a1b3155f0d62a90fa`.
  Retained GPL text, original credits, Intel firmware license and exact release
  identity are in `payloads/Kexts/Intel/KGP-1.0.0-*`.
  https://github.com/kgp-macPro/AirportItlwm-Tahoe/tree/v1.0.0 .
- **IntelBluetoothFirmware / IntelBTPatcher 2.5.0**: OpenIntelWireless project.
  The observed project's retained license is GPL version 3.
  Existing private baseline bundles report 2.5.0, while the observed official
  latest release/tag is `v2.4.0`; neither `v2.5.0` nor `2.5.0` resolves.
  Their exact corresponding-source revision is **unresolved**. These binaries
  must not be relabeled as an official release or redistributed on the assumption
  that the latest master is their matching source.
  https://github.com/OpenIntelWireless/IntelBluetoothFirmware .
  License notices are retained from observed master
  `a414375505fa3b014be32f8fca31b5bbfdf9f10f` for attribution, **not** as proof
  that this commit corresponds to either private 2.5.0 binary.
- **BlueToolFixup 2.7.2**: Acidanthera/BrcmPatchRAM,
  tag `2.7.2`, commit `aef376bb1e7e27cabc61da7edfb1a88fac7f7acc`.
  The GPL version 2 text is retained in `licenses/BrcmPatchRAM-LICENSE`;
  https://github.com/acidanthera/BrcmPatchRAM/tree/2.7.2 .

Existing upstream payloads and tools retain their respective licenses;
the patcher's license does not relicense Apple frameworks, firmware or bundled
kexts. PatcherSupportPkg 2.0.3 is obtained from its original official source,
not included as a new support DMG in this publication package.
