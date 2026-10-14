"""Public-checkout regressions; synthetic inputs, no macOS, network or drivers.

The existing Intel suite installs native-boundary stubs. GUI tests execute the
actual selected method bodies with a fake wx boundary, not rewritten logic.
"""
import ast
import copy
import hashlib
import importlib
import importlib.util
import json
import logging
import os
import plistlib
import sys
import tempfile
import types
import unittest
import zipfile
from pathlib import Path
from unittest import mock

import test_intel_tahoe as intel

ROOT = intel.ROOT
sys.path.insert(0, str(ROOT))
disk_images = importlib.import_module("ci_tooling.build_modules.disk_images")
updates = importlib.import_module(intel.PKG + ".support.updates")
payloads = importlib.import_module(intel.PKG + ".support.intel_wifi_payloads")
spec = importlib.util.spec_from_file_location("payload_importer", ROOT / "tools/import_intel_payloads.py")
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)


def gui_method(filename, class_name, method_name, **namespace):
    """Load actual GUI code while replacing only native/import boundaries."""
    tree = ast.parse((ROOT / "opencore_legacy_patcher/wx_gui" / filename).read_text())
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
    cls = copy.deepcopy(cls)
    cls.body = [next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == method_name)]
    module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), cls], type_ignores=[])
    scope = {"logging": logging, **namespace}
    exec(compile(ast.fix_missing_locations(module), filename, "exec"), scope)
    return scope[class_name]


class FakeFrame:
    def __init__(self, *args, **kwargs):
        self.destroyed = False

    def Close(self):
        self.destroyed = True

    def Destroy(self):
        self.destroyed = True


class UpdateIsolationTests(unittest.TestCase):
    def setUp(self):
        self.const = intel.Constants()
        self.wx = types.SimpleNamespace(Frame=FakeFrame, MessageBox=mock.Mock(),
                                        OK=1, ICON_INFORMATION=2, CallAfter=lambda fn: fn())

    def test_update_poll_never_queries_upstream_even_with_cached_result(self):
        checker = updates.CheckBinaryUpdates(self.const)
        checker.latest_details = {"Link": "https://example.invalid/upstream.pkg"}
        with mock.patch.object(updates.network_handler, "NetworkUtilities") as network:
            self.assertIsNone(checker.check_binary_updates())
            network.assert_not_called()

    def test_bootloader_version_comparison_is_not_disabled(self):
        checker = updates.CheckBinaryUpdates(self.const)
        self.assertTrue(checker.check_if_newer("99.0.0"))
        self.assertFalse(checker.check_if_newer("1.0.0"))
        self.assertFalse(self.const.special_build)

    def test_explicit_update_url_does_not_hide_parent_or_start_download(self):
        cls = gui_method("gui_update.py", "UpdateFrame", "__init__", wx=self.wx)
        parent = mock.Mock()
        frame = cls(parent, "Fork", self.const, None, "https://example.invalid/nightly.zip", "nightly")
        parent.Hide.assert_not_called()
        parent.GetChildren.assert_not_called()
        self.assertTrue(frame.destroyed)
        self.wx.MessageBox.assert_called_once()

    def test_parentless_update_frame_exits_cleanly(self):
        cls = gui_method("gui_update.py", "UpdateFrame", "__init__", wx=self.wx)
        self.assertTrue(cls(None, "Fork", self.const, None).destroyed)

    def test_direct_nightly_handler_returns_before_network(self):
        cls = gui_method("gui_settings.py", "SettingsFrame", "on_nightly", wx=self.wx)
        instance = cls()
        instance.constants = self.const
        instance.on_nightly(None)
        self.wx.MessageBox.assert_called_once()

    def test_installer_does_not_download_or_copy_cached_upstream_package(self):
        for method in ("_auto_package_handler", "_install_installer_pkg"):
            # No filesystem/network names in the namespace: accessing either
            # would fail, including when a stale cached AutoPkg is present.
            cls = gui_method("gui_macos_installer_flash.py", "macOSInstallerFlashFrame", method, wx=self.wx)
            instance = cls()
            instance.constants = self.const
            getattr(instance, method)(*([] if method == "_auto_package_handler" else ["disk9"]))


class IntelProfileBoundaryTests(unittest.TestCase):
    def test_unsupported_hosts_rejected_before_payload_access(self):
        helper = intel.IntelTahoeTests()
        for kernel in (0, 21, 22, 23, 26, 99):
            const = helper.constants(helper.card(), kernel=kernel)
            config = plistlib.loads((ROOT / "payloads/Config/config.plist").read_bytes())
            with mock.patch.object(payloads, "verify_pinned_payloads") as verify:
                with self.assertRaisesRegex(ValueError, "refusing to guess"):
                    intel.BuildWirelessNetworking("MacBookAir7,2", const, config)
                verify.assert_not_called()
            self.assertFalse(next(x for x in config["Kernel"]["Add"] if x["BundlePath"] == "AirportItlwm.kext")["Enabled"])

    def test_intel_root_patch_only_for_known_kernels(self):
        helper = intel.IntelTahoeTests()
        const = helper.constants(helper.card())
        for kernel in (22, 23, 24, 25, 26, 99):
            self.assertEqual(intel.ModernWireless(kernel, 0, "test", const).present(), kernel in (24, 25))

    def test_unsupported_hosts_do_not_relax_network_security_defaults(self):
        helper = intel.IntelTahoeTests()
        for kernel in (23, 26):
            const = helper.constants(helper.card(), kernel=kernel)
            obj = intel.GenerateDefaults.__new__(intel.GenerateDefaults)
            obj.model, obj.host_is_target, obj.constants = "MacBookAir7,2", True, const
            before = (const.sip_status, const.disable_cs_lv, const.disable_amfi)
            obj._networking_probe()
            self.assertEqual((const.sip_status, const.disable_cs_lv, const.disable_amfi), before)


class ImporterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source, self.dest = self.root / "inputs", self.root / "destination"
        self.source.mkdir()
        self.dest.mkdir()
        self.items = []
        for name in ("First", "Second"):
            archive = self.source / (name + ".zip")
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr(name + ".kext/Contents/Info.plist", plistlib.dumps({"CFBundleVersion": "1.0"}))
            self.items.append({"archive": archive.name, "bundle": name + ".kext", "version": "1.0",
                               "sha256": payloads.sha256_file(archive)})
        (self.dest / "manifest.json").write_text(json.dumps({"payloads": self.items}))

    def assert_no_published_archives(self):
        self.assertEqual(list(self.dest.glob("*.zip")), [])
        self.assertEqual(list(self.dest.glob("oclp-payload-check-*")), [])

    def test_success_and_repeat_preserve_existing_files(self):
        self.assertEqual(importer.import_payloads(self.source, self.dest), 2)
        first = self.dest / "First.zip"
        inode = first.stat().st_ino
        self.assertEqual(importer.import_payloads(self.source, self.dest), 2)
        self.assertEqual(first.stat().st_ino, inode)
        payloads.verify_pinned_payloads(self.dest)

    def test_missing_last_input_publishes_nothing(self):
        (self.source / "Second.zip").unlink()
        with self.assertRaisesRegex(ValueError, "Missing input"):
            importer.import_payloads(self.source, self.dest)
        self.assert_no_published_archives()

    def test_changed_last_input_publishes_nothing(self):
        with (self.source / "Second.zip").open("ab") as stream:
            stream.write(b"tampered")
        with self.assertRaisesRegex(ValueError, "changed"):
            importer.import_payloads(self.source, self.dest)
        self.assert_no_published_archives()

    def test_wrong_bundle_version_rejected_even_with_matching_hash(self):
        self.items[1]["version"] = "2.0"
        (self.dest / "manifest.json").write_text(json.dumps({"payloads": self.items}))
        with self.assertRaisesRegex(ValueError, "version mismatch"):
            importer.import_payloads(self.source, self.dest)
        self.assert_no_published_archives()

    def test_conflicting_destination_is_not_overwritten(self):
        target = self.dest / "Second.zip"
        target.write_bytes(b"existing file")
        with self.assertRaisesRegex(ValueError, "conflicting destination"):
            importer.import_payloads(self.source, self.dest)
        self.assertEqual(target.read_bytes(), b"existing file")
        self.assertFalse((self.dest / "First.zip").exists())

    def test_symlink_destination_is_not_followed(self):
        (self.dest / "Second.zip").symlink_to(self.source / "Second.zip")
        with self.assertRaisesRegex(ValueError, "conflicting destination"):
            importer.import_payloads(self.source, self.dest)
        self.assertFalse((self.dest / "First.zip").exists())

    def test_source_mutation_after_staging_cannot_change_published_bytes(self):
        real_link = os.link

        def mutate_then_link(src, dst):
            (self.source / "Second.zip").write_bytes(b"source changed after verification")
            return real_link(src, dst)

        with mock.patch.object(importer.os, "link", side_effect=mutate_then_link):
            importer.import_payloads(self.source, self.dest)
        payloads.verify_pinned_payloads(self.dest)

    def test_late_conflict_rolls_back_only_new_files(self):
        real_link = os.link

        def conflict_second(src, dst):
            if dst.name == "Second.zip":
                dst.write_bytes(b"concurrent writer")
            return real_link(src, dst)

        with mock.patch.object(importer.os, "link", side_effect=conflict_second):
            with self.assertRaisesRegex(ValueError, "appeared during import"):
                importer.import_payloads(self.source, self.dest)
        self.assertFalse((self.dest / "First.zip").exists())
        self.assertEqual((self.dest / "Second.zip").read_bytes(), b"concurrent writer")

    def test_manifest_path_traversal_is_rejected(self):
        self.items[0]["archive"] = "../outside.zip"
        (self.dest / "manifest.json").write_text(json.dumps({"payloads": self.items}))
        with self.assertRaisesRegex(ValueError, "local archive filenames"):
            importer.import_payloads(self.source, self.dest)
        self.assert_no_published_archives()


class BuildAssetTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        previous = Path.cwd()
        self.addCleanup(os.chdir, previous)
        os.chdir(self.tmp.name)
        self.good = b"synthetic official support image"
        self.const = intel.Constants()
        self.const.patcher_support_pkg_sha256 = hashlib.sha256(self.good).hexdigest()
        patch = mock.patch.object(disk_images.constants, "Constants", return_value=self.const)
        patch.start()
        self.addCleanup(patch.stop)

    def test_missing_payloads_stop_before_cleanup_or_download(self):
        folder = Path("payloads/Kexts/Intel")
        folder.mkdir(parents=True)
        (folder / "manifest.json").write_text(json.dumps({"payloads": [{"archive": "missing.zip"}]}))
        builder = disk_images.GenerateDiskImages()
        with mock.patch.object(builder, "_delete_extra_binaries") as cleanup, mock.patch.object(builder, "_download_resources") as download:
            with self.assertRaisesRegex(ValueError, "Missing fixed Intel payload"):
                builder.generate()
            cleanup.assert_not_called()
            download.assert_not_called()

    def test_payload_image_cache_is_rebuilt(self):
        Path("payloads.dmg").write_bytes(b"stale image without Intel drivers")
        with mock.patch.object(disk_images.subprocess_wrapper, "run_and_verify") as run:
            disk_images.GenerateDiskImages()._generate_payloads_dmg()
        self.assertTrue(any(call.args[0][:2] == ["/usr/bin/hdiutil", "create"] for call in run.call_args_list))

    def test_verified_support_cache_is_reused_without_network(self):
        Path("Universal-Binaries.dmg").write_bytes(self.good)
        with mock.patch.object(disk_images.subprocess_wrapper, "run_and_verify") as run:
            disk_images.GenerateDiskImages()._download_resources()
            run.assert_not_called()

    def test_invalid_cached_support_image_is_rejected(self):
        Path("Universal-Binaries.dmg").write_bytes(b"HTTP error page")
        with self.assertRaisesRegex(ValueError, "Cached.*SHA256 mismatch"):
            disk_images.GenerateDiskImages()._download_resources()

    def test_valid_download_promoted_after_hash_verification(self):
        def download(command, **kwargs):
            self.assertIn("--fail", command)
            self.assertTrue(command[-1].startswith("https://github.com/dortania/PatcherSupportPkg/"))
            Path(command[command.index("--output") + 1]).write_bytes(self.good)
        with mock.patch.object(disk_images.subprocess_wrapper, "run_and_verify", side_effect=download):
            disk_images.GenerateDiskImages()._download_resources()
        self.assertEqual(Path("Universal-Binaries.dmg").read_bytes(), self.good)
        self.assertFalse(Path("Universal-Binaries.dmg.part").exists())

    def test_bad_download_is_not_promoted_or_cached(self):
        def download(command, **kwargs):
            Path(command[command.index("--output") + 1]).write_bytes(b"incorrect bytes")
        with mock.patch.object(disk_images.subprocess_wrapper, "run_and_verify", side_effect=download):
            with self.assertRaisesRegex(ValueError, "Downloaded.*SHA256 mismatch"):
                disk_images.GenerateDiskImages()._download_resources()
        self.assertFalse(Path("Universal-Binaries.dmg").exists())
        self.assertFalse(Path("Universal-Binaries.dmg.part").exists())

    def test_interrupted_download_is_not_cached(self):
        def download(command, **kwargs):
            Path(command[command.index("--output") + 1]).write_bytes(b"partial")
            raise RuntimeError("connection interrupted")
        with mock.patch.object(disk_images.subprocess_wrapper, "run_and_verify", side_effect=download):
            with self.assertRaisesRegex(RuntimeError, "interrupted"):
                disk_images.GenerateDiskImages()._download_resources()
        self.assertFalse(Path("Universal-Binaries.dmg").exists())
        self.assertFalse(Path("Universal-Binaries.dmg.part").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
