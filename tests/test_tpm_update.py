import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("tpm_update", ROOT / "update-tpm.py")
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "Sistema"
        (self.repo / "host").mkdir(parents=True)
        self.settings = '{"username":"nexus","disk":"/dev/disk/by-id/real-ssd"}\n'
        (self.repo / "host/settings.json").write_text(self.settings)
        (self.repo / "host/hardware.nix").write_text("# actual HP hardware\n")
        for name in ("flake.nix", "flake.lock"):
            shutil.copyfile(ROOT / name, self.repo / name)
        self.uid_patch = patch.object(updater.os, "geteuid", return_value=1000)
        self.uid_patch.start()
        self.addCleanup(self.uid_patch.stop)

    def test_preserves_installed_identity_and_hardware_and_is_repeatable(self):
        updater.update(self.repo)
        updater.update(self.repo)
        self.assertEqual((self.repo / "host/settings.json").read_text(), self.settings)
        self.assertEqual((self.repo / "host/hardware.nix").read_text(), "# actual HP hardware\n")
        self.assertEqual((self.repo / "modules/secure-boot.nix").read_bytes(),
                         (ROOT / "modules/secure-boot.nix").read_bytes())

    def test_refuses_user_changes_before_any_copy(self):
        original = (self.repo / "flake.nix").read_bytes()
        (self.repo / "flake.lock").write_text("user changes")
        with self.assertRaisesRegex(RuntimeError, "cambios propios"):
            updater.update(self.repo)
        self.assertEqual((self.repo / "flake.nix").read_bytes(), original)
        self.assertFalse((self.repo / "modules/secure-boot.nix").exists())

    def test_refuses_template_destination(self):
        (self.repo / "host/settings.json").write_text(json.dumps({
            "disk": "/dev/disk/by-id/INSTALLER-MUST-SELECT-A-DISK"}))
        with self.assertRaisesRegex(RuntimeError, "plantilla"):
            updater.update(self.repo)
        self.assertFalse((self.repo / "modules/secure-boot.nix").exists())


if __name__ == "__main__":
    unittest.main()
