"""Safety regression tests. No commands touching real disks are executed."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


installer = load("installer", ROOT / "installer/install.py")
seed = load("seed", ROOT / "scripts/seed.py")


def disk():
    return {"name": "/dev/nvme0n1", "size": 512 * 1024**3,
            "type": "disk", "model": "TEST DISK", "serial": "TEST123",
            "wwn": "test", "maj:min": "259:0", "ro": False,
            "rm": False, "tran": "nvme", "mountpoints": [None],
            "children": [{"name": "/dev/nvme0n1p1", "type": "part", "mountpoints": [None]}]}


class DiskSelection(unittest.TestCase):
    def test_internal_unmounted_candidate(self):
        self.assertIsNone(installer.rejection(disk()))

    def test_usb_removable_readonly_small_and_partition_rejected(self):
        for changes in [{"tran": "usb"}, {"rm": True}, {"ro": True},
                        {"size": 1024}, {"type": "part"}]:
            with self.subTest(changes=changes):
                d = disk()
                d.update(changes)
                self.assertIsNotNone(installer.rejection(d))

    def test_mounted_descendants_and_swap_rejected(self):
        for mount in ["/", "/iso", "/home", "/mnt", "[SWAP]"]:
            with self.subTest(mount=mount):
                d = disk()
                d["children"][0]["mountpoints"] = [mount]
                self.assertIsNotNone(installer.rejection(d))

    def test_open_luks_lvm_raid_rejected(self):
        for kind in ["crypt", "lvm", "raid1"]:
            d = disk()
            d["children"][0]["children"] = [{"name": "/dev/mapper/test", "type": kind}]
            self.assertIsNotNone(installer.rejection(d))

    def test_disk_changed_during_build_rejected(self):
        original = disk()
        changed = copy.deepcopy(original)
        changed["serial"] = "DIFFERENT"
        with patch.object(installer, "disk_inventory", return_value=[changed]):
            with self.assertRaises(RuntimeError):
                installer.verify_selected(original, "/dev/disk/by-id/test")

    def test_disk_mounted_during_build_rejected(self):
        original = disk()
        changed = copy.deepcopy(original)
        changed["children"][0]["mountpoints"] = ["/media/new"]
        with patch.object(installer, "disk_inventory", return_value=[changed]):
            with self.assertRaises(RuntimeError):
                installer.verify_selected(original, "/dev/disk/by-id/test")

    def test_confirmation_requires_exact_stable_path(self):
        for response in ["", "yes", "si", "BORRAR", "BORRAR /dev/sda"]:
            with patch("builtins.input", return_value=response):
                self.assertFalse(installer.confirm_erase("/dev/disk/by-id/test"))
        with patch("builtins.input", return_value="BORRAR /dev/disk/by-id/test"):
            self.assertTrue(installer.confirm_erase("/dev/disk/by-id/test"))

    def test_cancel_never_runs_a_command_or_creates_secret(self):
        with tempfile.TemporaryDirectory() as temp:
            secret = Path(temp) / "secret"
            with patch.object(installer, "SECRET_DIR", secret), \
                 patch.object(installer, "password", return_value="test-password"), \
                 patch.object(installer, "confirm_erase", return_value=False), \
                 patch.object(installer, "run") as runner:
                installer.install(disk(), "/dev/disk/by-id/test", Path(temp), {}, "/fake/disko")
                runner.assert_not_called()
                self.assertFalse(secret.exists())

    def test_device_recheck_precedes_destruction(self):
        with patch.object(installer, "password", return_value="test-password"), \
             patch.object(installer, "confirm_erase", return_value=True), \
             patch.object(installer, "verify_selected", side_effect=RuntimeError("changed")), \
             patch.object(installer, "run") as runner:
            with self.assertRaises(RuntimeError):
                installer.install(disk(), "/dev/disk/by-id/test", Path("/unused"), {}, "/fake/disko")
            runner.assert_not_called()

    def test_key_removed_when_partitioning_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            secret = Path(temp) / "secret"
            def failing_run(_args, **_kwargs):
                key = secret / "luks.key"
                self.assertEqual(key.read_text(), "test-password")
                self.assertEqual(key.stat().st_mode & 0o777, 0o600)
                raise RuntimeError("simulated disko failure")
            with patch.object(installer, "SECRET_DIR", secret), \
                 patch.object(installer, "password", return_value="test-password"), \
                 patch.object(installer, "confirm_erase", return_value=True), \
                 patch.object(installer, "verify_selected"), \
                 patch.object(installer, "require_target_free"), \
                 patch.object(installer, "run", side_effect=failing_run):
                with self.assertRaises(RuntimeError):
                    installer.install(disk(), "/dev/disk/by-id/test", Path(temp), {}, "/fake/disko")
            self.assertFalse(secret.exists())

    def test_target_mount_appearing_after_downloads_prevents_partitioning(self):
        with patch.object(installer, "password", return_value="test-password"), \
             patch.object(installer, "confirm_erase", return_value=True), \
             patch.object(installer, "verify_selected"), \
             patch.object(installer, "require_target_free", side_effect=RuntimeError("occupied")), \
             patch.object(installer, "run") as runner:
            with self.assertRaisesRegex(RuntimeError, "occupied"):
                installer.install(disk(), "/dev/disk/by-id/test", Path("/unused"), {}, "/fake/disko")
            runner.assert_not_called()

    def test_non_root_refused(self):
        with patch.object(installer.os, "geteuid", return_value=1000):
            with self.assertRaises(RuntimeError):
                installer.require_live_environment()


class WritableSettings(unittest.TestCase):
    def test_defaults_are_idempotent_and_preserve_user_edits(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            args = [home, ROOT / "desktop/dms.json", ROOT / "docs/AGENTS-global.md",
                    ROOT / "docs/AGENTS-study.md"]
            seed.seed(*args)
            settings = home / ".config/DankMaterialShell/settings.json"
            settings.write_text('{"personal": true}')
            progress = home / "Estudio/AI-Security/PROGRESO.md"
            progress.write_text("My progress")
            seed.seed(*args)
            self.assertEqual(settings.read_text(), '{"personal": true}')
            self.assertEqual(progress.read_text(), "My progress")


if __name__ == "__main__":
    unittest.main()
