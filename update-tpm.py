"""Copy only the TPM addition into an existing installation; never change host data."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

SOURCE = Path(__file__).resolve().parent
FILES = ("flake.nix", "flake.lock", "modules/secure-boot.nix", "docs/TPM-SECURE-BOOT.md")


def update(destination):
    destination = Path(destination).resolve()
    if os.geteuid() == 0:
        raise RuntimeError("Ejecuta como tu usuario, sin sudo.")
    if destination == SOURCE:
        raise RuntimeError("El destino debe ser tu repositorio instalado, no este USB.")
    settings_path = destination / "host/settings.json"
    settings = json.loads(settings_path.read_text())
    if settings.get("disk") == "/dev/disk/by-id/INSTALLER-MUST-SELECT-A-DISK":
        raise RuntimeError("El destino es una plantilla, no la configuracion instalada.")
    baseline = json.loads((SOURCE / "docs/tpm-upgrade-baseline.json").read_text())
    for name in FILES:
        target = destination / name
        if target.is_symlink():
            raise RuntimeError(f"No sustituyo un enlace: {name}")
        if target.exists():
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            new_digest = hashlib.sha256((SOURCE / name).read_bytes()).hexdigest()
            if digest not in (baseline.get(name), new_digest):
                raise RuntimeError(f"Hay cambios propios en {name}; integrarlos manualmente.")
        if target.parent.resolve().is_relative_to(destination) is False:
            raise RuntimeError(f"Ruta fuera del repositorio: {name}")
    # Validate every file before copying any. Host identity and hardware are untouched.
    for name in FILES:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE / name, target)
    print("Actualizacion copiada. Usuario, disco y hardware conservados.")
    print("Sigue ~/Sistema/docs/TPM-SECURE-BOOT.md; no se ha activado ningun cambio.")


if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            raise RuntimeError('Uso: python3 update-tpm.py "$HOME/Sistema"')
        update(sys.argv[1])
    except (OSError, ValueError, RuntimeError) as error:
        sys.exit(f"ERROR: {error}")
