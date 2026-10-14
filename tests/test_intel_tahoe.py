"""Exercise real fork code on Linux without importing the macOS GUI.

Only native IOKit/NVRAM boundaries are stubbed. No root patch is executed.
"""
import importlib
import importlib.util
import json
import plistlib
import shutil
import sys
import tempfile
import types
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = 'opencore_legacy_patcher'
for name, path in [
    (PKG, ROOT / PKG),
    (PKG + '.detections', ROOT / PKG / 'detections'),
    (PKG + '.datasets', ROOT / PKG / 'datasets'),
    (PKG + '.support', ROOT / PKG / 'support'),
    (PKG + '.efi_builder', ROOT / PKG / 'efi_builder'),
    (PKG + '.efi_builder.networking', ROOT / PKG / 'efi_builder/networking'),
    (PKG + '.sys_patch', ROOT / PKG / 'sys_patch'),
    (PKG + '.sys_patch.patchsets', ROOT / PKG / 'sys_patch/patchsets'),
    (PKG + '.sys_patch.patchsets.hardware', ROOT / PKG / 'sys_patch/patchsets/hardware'),
    (PKG + '.sys_patch.patchsets.hardware.networking', ROOT / PKG / 'sys_patch/patchsets/hardware/networking'),
]:
    mod = types.ModuleType(name)
    mod.__path__ = [str(path)]
    sys.modules[name] = mod
ioreg = types.ModuleType(PKG + '.detections.ioreg')
ioreg.io_registry_entry_t = int
sys.modules[ioreg.__name__] = ioreg
utilities = types.ModuleType(PKG + '.support.utilities')
utilities.friendly_hex = lambda x: f'{x:04X}'
sys.modules[utilities.__name__] = utilities

device_probe = importlib.import_module(PKG + '.detections.device_probe')
Constants = importlib.import_module(PKG + '.constants').Constants
ModernWireless = importlib.import_module(PKG + '.sys_patch.patchsets.hardware.networking.modern_wireless').ModernWireless
BuildWirelessNetworking = importlib.import_module(PKG + '.efi_builder.networking.wireless').BuildWirelessNetworking
BuildSupport = importlib.import_module(PKG + '.efi_builder.support').BuildSupport
GenerateDefaults = importlib.import_module(PKG + '.support.defaults').GenerateDefaults
verify_pinned_payloads = importlib.import_module(PKG + '.support.intel_wifi_payloads').verify_pinned_payloads
pci_data = importlib.import_module(PKG + '.datasets.pci_data')


class IntelTahoeTests(unittest.TestCase):
    def card(self, device=0x2725):
        return device_probe.IntelWirelessCard(0x8086, device, 0x028000)

    def constants(self, card, kernel=25):
        const = Constants()
        const.current_path = ROOT
        const.payload_path = ROOT / 'payloads'
        const.computer = device_probe.Computer()
        const.computer.wifi = card
        const.detected_os = kernel
        return const

    def test_vendor_selection_without_spoof(self):
        raw = device_probe.PCIDevice(0x8086, 0x2725, 0x028000)
        self.assertIs(raw.vendor_detect(inherits=device_probe.WirelessCard), device_probe.IntelWirelessCard)
        ethernet = device_probe.PCIDevice(0x8086, 0x2725, 0x020000)
        self.assertIsNone(ethernet.vendor_detect(inherits=device_probe.WirelessCard))

    def test_allowlist_matches_frozen_driver_not_all_intel(self):
        with zipfile.ZipFile(ROOT / 'payloads/Kexts/Intel/AirportItlwm-Ventura-v2.3.0.zip') as z:
            info = plistlib.loads(z.read('AirportItlwm.kext/Contents/Info.plist'))
        expected = {int(x, 16) >> 16 for x in info['IOKitPersonalities']['itlwm']['IOPCIMatch'].split()}
        self.assertEqual(set(pci_data.intelwl_ids.IntelWirelessIDs), expected)
        self.assertEqual(len(expected), 87)
        with zipfile.ZipFile(ROOT / 'payloads/Kexts/Intel/AirportItlwm-Tahoe-v1.0.0.zip') as z:
            info = plistlib.loads(z.read('AirportItlwm.kext/Contents/Info.plist'))
        tahoe_ids = {int(x, 16) >> 16 for x in info['IOKitPersonalities']['itlwm']['IOPCIMatch'].split()}
        self.assertEqual(tahoe_ids, expected)
        for devid in expected:
            self.assertEqual(self.card(devid).chipset, device_probe.IntelWirelessCard.Chipsets.IntelWirelessIDs)
        self.assertEqual(self.card(0x272B).chipset, device_probe.IntelWirelessCard.Chipsets.Unknown)

    def test_tahoe_and_sequoia_select_intel_root_patch(self):
        const = self.constants(self.card())
        for kernel in [24, 25]:
            patch = ModernWireless(kernel, 0, 'test', const)
            self.assertTrue(patch.present())
            self.assertFalse(patch.native_os())
            self.assertIn('Intel Wireless', patch.name())
            patches = patch.patches()
            self.assertEqual(set(patches), {'Modern Wireless Common'})
            entries = [v for section in patches.values() for operation in section.values()
                       for directory in operation.values() for v in directory.values()]
            self.assertEqual(entries, [f'13.7.2-{kernel}'] * 3)
        self.assertFalse(ModernWireless(23, 0, 'test', const).present())

    def test_unknown_no_wifi_and_broadcom_regression(self):
        for wifi in [None, self.card(0xFFFF)]:
            self.assertFalse(ModernWireless(25, 0, 'test', self.constants(wifi)).present())
        broadcom = device_probe.Broadcom(0x14E4, 0x43A0, 0x028000)
        patch = ModernWireless(25, 0, 'test', self.constants(broadcom))
        self.assertTrue(patch.present())
        self.assertEqual(patch.name(), 'Networking: Modern Wireless')

    def test_frozen_payloads_validated_and_tampering_rejected(self):
        folder = ROOT / 'payloads/Kexts/Intel'
        verify_pinned_payloads(folder)
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp)
            shutil.copytree(folder, copy, dirs_exist_ok=True)
            archive = copy / 'IntelBTPatcher-v2.5.0.zip'
            archive.write_bytes(archive.read_bytes() + b'changed')
            with self.assertRaisesRegex(ValueError, 'changed'):
                verify_pinned_payloads(copy)

    def test_real_wireless_builder_supplies_stack_and_locked_drivers(self):
        const = self.constants(self.card())
        config = plistlib.loads((ROOT / 'payloads/Config/config.plist').read_bytes())
        with tempfile.TemporaryDirectory() as tmp:
            const.current_path = Path(tmp)
            const.opencore_release_folder.mkdir(parents=True)
            const.kexts_path.mkdir(parents=True)
            BuildWirelessNetworking('MacBookAir7,2', const, config)
            paths = [x['BundlePath'] for x in config['Kernel']['Add']]
            self.assertEqual(len(paths), len(set(paths)), 'duplicate kext entries')
            rows = {x['BundlePath']: x for x in config['Kernel']['Add']}
            for bundle in ['IOSkywalkFamily.kext', 'IO80211FamilyLegacy.kext', 'AirportItlwm.kext',
                           'IntelBluetoothFirmware.kext', 'IntelBTPatcher.kext', 'BlueToolFixup.kext']:
                self.assertTrue(rows[bundle]['Enabled'], bundle)
            self.assertFalse(rows['AirPortBrcmNIC-Tahoe.kext']['Enabled'])
            self.assertFalse(rows['IO80211FamilyLegacy.kext/Contents/PlugIns/AirPortBrcmNIC.kext']['Enabled'])
            block = next(x for x in config['Kernel']['Block'] if x['Identifier'] == 'com.apple.iokit.IOSkywalkFamily')
            self.assertTrue(block['Enabled'])
            self.assertFalse(config['DeviceProperties']['Add'])
            nvram = config['NVRAM']['Add']['7C436110-AB2A-4BBB-A880-FE41995C9F82']
            self.assertEqual(nvram['bluetoothExternalDongleFailed'], bytes(1))
            self.assertEqual(nvram['bluetoothInternalControllerInfo'], bytes(14))
            for archive in const.kexts_path.glob('*.zip'):
                with zipfile.ZipFile(archive) as z:
                    z.extractall(const.kexts_path)
            for name, version in [('AirportItlwm', '1.0.0'), ('IntelBluetoothFirmware', '2.5.0'), ('IntelBTPatcher', '2.5.0')]:
                info = plistlib.loads((const.kexts_path / (name + '.kext') / 'Contents/Info.plist').read_bytes())
                self.assertEqual(info['CFBundleVersion'], version)
            self.assertEqual(rows['AirportItlwm.kext']['MinKernel'], '25.0.0')
            self.assertEqual(rows['AirportItlwm.kext']['MaxKernel'], '25.99.99')
            self.assertFalse(config['Kernel']['Quirks']['DisableIoMapper'])
            order = [x['BundlePath'] for x in config['Kernel']['Add']]
            self.assertLess(order.index('Lilu.kext'), order.index('IntelBTPatcher.kext'))
            self.assertLess(order.index('IOSkywalkFamily.kext'), order.index('IO80211FamilyLegacy.kext'))
            self.assertLess(order.index('IO80211FamilyLegacy.kext'), order.index('AirportItlwm.kext'))

    def test_sequoia_retains_ventura_payload(self):
        const = self.constants(self.card(), kernel=24)
        config = plistlib.loads((ROOT / 'payloads/Config/config.plist').read_bytes())
        with tempfile.TemporaryDirectory() as tmp:
            const.current_path = Path(tmp)
            const.opencore_release_folder.mkdir(parents=True)
            const.kexts_path.mkdir(parents=True)
            BuildWirelessNetworking('MacBookAir7,2', const, config)
            with zipfile.ZipFile(const.kexts_path / 'AirportItlwm-Ventura-v2.3.0.zip') as z:
                info = plistlib.loads(z.read('AirportItlwm.kext/Contents/Info.plist'))
            self.assertEqual(info['CFBundleVersion'], '2.3.0')
            self.assertFalse((const.kexts_path / 'AirportItlwm-Tahoe-v1.0.0.zip').exists())
            airport = next(row for row in config['Kernel']['Add'] if row['BundlePath'] == 'AirportItlwm.kext')
            self.assertEqual(airport['MinKernel'], '24.0.0')
            self.assertEqual(airport['MaxKernel'], '24.99.99')

    def test_tahoe_payload_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            shutil.copytree(ROOT / 'payloads/Kexts/Intel', folder, dirs_exist_ok=True)
            p = folder / 'AirportItlwm-Tahoe-v1.0.0.zip'
            p.write_bytes(p.read_bytes() + b'changed')
            with self.assertRaisesRegex(ValueError, 'changed'):
                verify_pinned_payloads(folder)

    def test_unknown_intel_does_not_supply_drivers(self):
        const = self.constants(self.card(0xFFFF))
        config = plistlib.loads((ROOT / 'payloads/Config/config.plist').read_bytes())
        BuildWirelessNetworking('MacBookAir7,2', const, config)
        self.assertFalse(next(x for x in config['Kernel']['Add'] if x['BundlePath'] == 'AirportItlwm.kext')['Enabled'])

    def test_real_cleanup_removes_only_expected_intel_broadcom_plugin(self):
        const = self.constants(self.card())
        config = plistlib.loads((ROOT / 'payloads/Config/config.plist').read_bytes())
        with tempfile.TemporaryDirectory() as tmp:
            const.current_path = Path(tmp)
            const.kexts_path.mkdir(parents=True)
            const.opencore_zip_copied.touch()
            BuildWirelessNetworking('MacBookAir7,2', const, config)
            BuildSupport('MacBookAir7,2', const, config).cleanup()
            self.assertFalse((const.kexts_path / 'IO80211FamilyLegacy.kext/Contents/PlugIns/AirPortBrcmNIC.kext').exists())
            self.assertTrue((const.kexts_path / 'AirportItlwm.kext/Contents/Info.plist').is_file())

    def test_cleanup_still_rejects_unknown_plugin_in_intel_profile(self):
        const = self.constants(self.card())
        config = plistlib.loads((ROOT / 'payloads/Config/config.plist').read_bytes())
        with tempfile.TemporaryDirectory() as tmp:
            const.current_path = Path(tmp)
            const.kexts_path.mkdir(parents=True)
            const.opencore_zip_copied.touch()
            BuildWirelessNetworking('MacBookAir7,2', const, config)
            (const.kexts_path / 'Other.kext/Contents/PlugIns/Unknown.kext').mkdir(parents=True)
            with self.assertRaisesRegex(Exception, 'Unknown plugin found: Unknown.kext'):
                BuildSupport('MacBookAir7,2', const, config).cleanup()

    def test_cleanup_does_not_allow_broadcom_plugin_on_unknown_intel(self):
        const = self.constants(self.card(0xFFFF))
        config = plistlib.loads((ROOT / 'payloads/Config/config.plist').read_bytes())
        with tempfile.TemporaryDirectory() as tmp:
            const.current_path = Path(tmp)
            (const.kexts_path / 'IO80211FamilyLegacy.kext/Contents/PlugIns/AirPortBrcmNIC.kext').mkdir(parents=True)
            const.opencore_zip_copied.touch()
            with self.assertRaisesRegex(Exception, 'Unknown plugin found: AirPortBrcmNIC.kext'):
                BuildSupport('MacBookAir7,2', const, config).cleanup()

    def test_network_security_defaults_include_intel(self):
        const = self.constants(self.card())
        instance = GenerateDefaults.__new__(GenerateDefaults)
        instance.model = 'MacBookAir7,2'
        instance.host_is_target = True
        instance.constants = const
        instance._networking_probe()
        self.assertFalse(const.sip_status)
        self.assertTrue(const.disable_cs_lv)
        self.assertTrue(const.disable_amfi)


if __name__ == '__main__':
    unittest.main(verbosity=2)
