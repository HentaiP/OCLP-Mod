"""
disk_images.py: Fetch and generate disk images (Universal-Binaries.dmg, payloads.dmg)
"""

import subprocess

from pathlib import Path

from opencore_legacy_patcher import constants
from opencore_legacy_patcher.support import subprocess_wrapper, intel_wifi_payloads



class GenerateDiskImages:

    def __init__(self, reset_dmg_cache: bool = False) -> None:
        """
        Initialize
        """
        self.reset_dmg_cache = reset_dmg_cache


    def _delete_extra_binaries(self):
        """
        Delete extra binaries from payloads directory
        """

        whitelist_folders = [
            "ACPI",
            "Config",
            "Drivers",
            "Icon",
            "Kexts",
            "OpenCore",
            "Tools",
            "Launch Services",
        ]

        whitelist_files = []

        print("Deleting extra binaries...")
        for file in Path("payloads").glob(pattern="*"):
            if file.is_dir():
                if file.name in whitelist_folders:
                    continue
                print(f"- Deleting {file.name}")
                subprocess_wrapper.run_and_verify(["/bin/rm", "-rf", file])
            else:
                if file.name in whitelist_files:
                    continue
                print(f"- Deleting {file.name}")
                subprocess_wrapper.run_and_verify(["/bin/rm", "-f", file])



    def _generate_payloads_dmg(self):
        """
        Generate disk image containing all payloads
        Disk image will be password protected due to issues with
        Apple's notarization system and inclusion of kernel extensions
        """

        if Path("./payloads.dmg").exists():
            # The source-only checkout gains Intel inputs after import. An old
            # image may omit them or contain a previous profile; always rebuild
            # this local image from the just-verified payload directory.
            print("- Removing old payloads.dmg")
            subprocess_wrapper.run_and_verify(
                ["/bin/rm", "-rf", "./payloads.dmg"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

        print("Generating DMG...")
        subprocess_wrapper.run_and_verify([
            '/usr/bin/hdiutil', 'create', './payloads.dmg',
            '-megabytes', '32000',  # Overlays can only be as large as the disk image allows
            '-format', 'UDZO', '-ov',
            '-volname', 'OpenCore Patcher Resources (Base)',
            '-fs', 'HFS+',
            '-layout', 'NONE',
            '-srcfolder', './payloads',
            '-passphrase', 'password', '-encryption'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print("DMG generation complete")


    def _download_resources(self):
        """
        Download required dependencies
        """

        build_constants = constants.Constants()
        patcher_support_pkg_version = build_constants.patcher_support_pkg_version
        expected_hash = build_constants.patcher_support_pkg_sha256
        required_resources = [
            "Universal-Binaries.dmg"
        ]

        print("Downloading required resources...")
        for resource in required_resources:
            if Path(f"./{resource}").exists():
                if self.reset_dmg_cache is True:
                    print(f"  - Removing old {resource}")
                    # Just to be safe
                    assert resource, "Resource cannot be empty"
                    assert resource not in ("/", "."), "Resource cannot be root"
                    subprocess_wrapper.run_and_verify(
                        ["/bin/rm", "-rf", f"./{resource}"],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE
                    )
                else:
                    if intel_wifi_payloads.sha256_file(Path(resource)) != expected_hash:
                        raise ValueError(f"Cached {resource} SHA256 mismatch; use --reset-dmg-cache to redownload")
                    print(f"- {resource} SHA256 verified, skipping download")
                    continue

            print(f"- Downloading {resource}...")

            # Never promote HTTP error pages or interrupted downloads to a
            # reusable support image. The original official URL is preserved.
            partial = Path(resource + ".part")
            try:
                subprocess_wrapper.run_and_verify(
                    ["/usr/bin/curl", "--fail", "--location", "--output", str(partial),
                     f"https://github.com/dortania/PatcherSupportPkg/releases/download/{patcher_support_pkg_version}/{resource}"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                if intel_wifi_payloads.sha256_file(partial) != expected_hash:
                    raise ValueError(f"Downloaded {resource} SHA256 mismatch")
                partial.replace(resource)
            finally:
                partial.unlink(missing_ok=True)


    def generate(self) -> None:
        """
        Generate disk images
        """

        # Reject an incomplete source checkout before downloads or cleanup.
        intel_wifi_payloads.verify_pinned_payloads(Path("payloads/Kexts/Intel"))
        self._delete_extra_binaries()
        self._generate_payloads_dmg()
        self._download_resources()
