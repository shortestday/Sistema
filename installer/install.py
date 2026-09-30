#!/usr/bin/env python3
"""Interactive whole-disk installer. No unattended erase and no default disk."""
import argparse
import fcntl
import getpass
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

SOURCE = Path(__file__).resolve().parents[1]
CACHE_OPTIONS = [
    "--option", "extra-substituters", "https://cache.numtide.com",
    "--option", "extra-trusted-public-keys",
    "niks3.numtide.com-1:DTx8wZduET09hRmMtKdQDxNNthLQETkc/yaX7M4qK0g=",
]
NIX = ["nix", "--extra-experimental-features", "nix-command flakes", *CACHE_OPTIONS]
SECRET_DIR = Path("/run/personal-os-installer")
MOUNT = Path("/mnt")


def run(args, capture=False, **kwargs):
    result = subprocess.run(args, check=True, text=True,
                            stdout=subprocess.PIPE if capture else None, **kwargs)
    return result.stdout.strip() if capture else None


def nodes(device):
    yield device
    for child in device.get("children", []):
        yield from nodes(child)


def rejection(device):
    if device.get("type") != "disk":
        return "no es un disco completo"
    if device.get("ro") or device.get("rm") or device.get("tran") == "usb":
        return "USB, extraible o solo lectura"
    if int(device.get("size", 0)) < 64 * 1024**3:
        return "menos de 64 GiB"
    for node in nodes(device):
        if any(node.get("mountpoints") or []):
            return "contiene sistemas montados o swap activo"
        if node.get("type") not in ("disk", "part"):
            return "tiene dispositivos dependientes (LUKS/LVM/RAID) abiertos"
    return None


def disk_inventory():
    raw = run(["lsblk", "--json", "--bytes", "--paths", "--output",
               "NAME,TYPE,SIZE,MODEL,SERIAL,WWN,TRAN,RM,RO,MOUNTPOINTS,MAJ:MIN"], True)
    return json.loads(raw)["blockdevices"]


def fingerprint(device):
    return tuple(device.get(key) for key in ["name", "size", "model", "serial", "wwn", "maj:min"])


def stable_path(device):
    target = Path(device["name"]).resolve()
    paths = sorted(Path("/dev/disk/by-id").glob("*"))
    for path in paths:
        if "-part" not in path.name and path.is_symlink() and path.resolve() == target:
            return str(path)
    raise RuntimeError("El disco no tiene identificador estable /dev/disk/by-id. Se cancela.")


def verify_selected(original, disk_id):
    matches = [d for d in disk_inventory() if fingerprint(d) == fingerprint(original)]
    if len(matches) != 1 or rejection(matches[0]):
        raise RuntimeError("El disco ha cambiado o ahora esta ocupado. Se cancela.")
    if Path(disk_id).resolve() != Path(original["name"]).resolve():
        raise RuntimeError("El identificador del disco ha cambiado. Se cancela.")
    for node in nodes(matches[0]):
        holders = Path("/sys/class/block") / Path(node["name"]).name / "holders"
        if holders.exists() and any(holders.iterdir()):
            raise RuntimeError("Hay dispositivos dependientes activos en el disco. Se cancela.")


def require_target_free():
    occupied = subprocess.run(["findmnt", "-rn", "--mountpoint", str(MOUNT)], capture_output=True)
    if occupied.returncode == 0 or (MOUNT.exists() and any(MOUNT.iterdir())):
        raise RuntimeError("/mnt esta ocupado. Usa una sesion live limpia; no se desmontara nada automaticamente.")
    if Path("/dev/mapper/cryptroot").exists():
        raise RuntimeError("Ya existe un volumen cryptroot abierto. Se cancela.")


def require_live_environment():
    if os.geteuid() != 0:
        raise RuntimeError("Ejecuta mediante sudo o install.sh.")
    if not Path("/sys/firmware/efi").exists():
        raise RuntimeError("Arranca el USB en modo UEFI. BIOS heredado no esta soportado.")
    release = Path("/etc/os-release").read_text()
    if not re.search(r'^ID=[\"\']?nixos[\"\']?$', release, re.M):
        raise RuntimeError("Este instalador solo se ejecuta en el USB oficial de NixOS.")
    live = False
    for mount, allowed in [("/iso", "iso9660"), ("/nix/.ro-store", "squashfs")]:
        check = subprocess.run(["findmnt", "-rn", "--mountpoint", mount, "-o", "FSTYPE"],
                               text=True, capture_output=True)
        live |= check.returncode == 0 and check.stdout.strip() == allowed
    if not live:
        raise RuntimeError("No se detecta el medio live de NixOS. No se permite instalar desde el sistema habitual.")
    require_target_free()
    for executable in ["nixos-install", "nixos-generate-config", "nixos-enter", "nix", "lsblk"]:
        if not shutil.which(executable):
            raise RuntimeError(f"Falta {executable}; utiliza una ISO oficial reciente de NixOS.")


def ask(label, default, pattern):
    value = input(f"{label} [{default}]: ").strip() or default
    if not re.fullmatch(pattern, value):
        raise RuntimeError(f"Valor no valido: {label}")
    return value


def password(label):
    first = getpass.getpass(label + ": ")
    second = getpass.getpass("Repite la contraseña: ")
    if first != second or len(first) < 10 or any(c in first for c in "\n\r\x00"):
        raise RuntimeError("Las contraseñas deben coincidir y tener al menos 10 caracteres.")
    return first


def confirm_erase(disk_id):
    phrase = f"BORRAR {disk_id}"
    print("\nSe eliminaran TODAS las particiones y TODOS los datos de este disco.")
    print("No conserva Windows ni otro sistema. Requiere copia previa de tus datos.")
    print(f"Para autorizarlo escribe exactamente: {phrase}")
    return input("> ").strip() == phrase


def describe(devices):
    for index, device in enumerate(devices, 1):
        reason = rejection(device)
        size = int(device.get("size", 0)) / 1024**3
        print(f"{index}. {device['name']} | {size:.1f} GiB | {device.get('model')} | serie: {device.get('serial')}")
        print("   " + ("NO seleccionable: " + reason if reason else "Candidato interno; elegirlo borrara su contenido"))


def prepare(device, disk_id):
    stage = Path(tempfile.mkdtemp(prefix="personal-os-")) / "config"
    shutil.copytree(SOURCE, stage, ignore=shutil.ignore_patterns(".git", "__pycache__", "result"))
    settings = json.loads((stage / "host/settings.json").read_text())
    # Provision keys on the installed HP. Never seal a TPM key from the live USB.
    settings["secureBoot"] = False
    settings["tpmUnlock"] = False
    settings["disk"] = disk_id
    settings["username"] = ask("Usuario", settings["username"], r"[a-z][a-z0-9_-]{0,30}")
    if settings["username"] in {"root", "nixos", "nobody", "sddm"}:
        raise RuntimeError("Ese usuario esta reservado.")
    settings["hostname"] = ask("Nombre del equipo", settings["hostname"], r"[a-z][a-z0-9-]{0,62}")
    settings["keyboard"] = ask("Teclado (es/us)", settings["keyboard"], r"es|us")
    settings["locale"] = ask("Idioma (es_ES.UTF-8/en_US.UTF-8)", settings["locale"], r"es_ES\.UTF-8|en_US\.UTF-8")
    settings["timezone"] = ask("Zona horaria", settings["timezone"], r"[A-Za-z_]+(?:/[A-Za-z_+-]+)+")
    if not (Path("/etc/zoneinfo") / settings["timezone"]).exists() and not (Path("/usr/share/zoneinfo") / settings["timezone"]).exists():
        # ZoneInfo also searches NixOS's TZDIR when set.
        from zoneinfo import ZoneInfo
        ZoneInfo(settings["timezone"])
    (stage / "host/settings.json").write_text(json.dumps(settings, indent=2) + "\n")
    hardware = run(["nixos-generate-config", "--show-hardware-config", "--no-filesystems"], True)
    (stage / "host/hardware.nix").write_text(hardware + "\n")
    print(f"\nConfiguracion preparada en {stage}")
    print("Validando opciones y calculando descargas. Aun no se modifica el disco.")
    ref = f"path:{stage}#nixosConfigurations.elitebook.config.system.build"
    run(NIX + ["eval", ref + ".toplevel.drvPath", "--raw", "--no-update-lock-file"])
    run(NIX + ["build", ref + ".toplevel", "--dry-run", "--no-link", "--no-update-lock-file"])
    # Only fetch the small partitioning toolchain before erasing; the whole OS
    # might exceed the live USB's RAM-backed store. nixos-install builds on disk.
    disko = run(NIX + ["build", ref + ".diskoScript", "--no-link", "--print-out-paths",
                      "--no-update-lock-file"], True)
    if not re.fullmatch(r"/nix/store/[^\s]+", disko):
        raise RuntimeError("Ruta de Disko inesperada; no se ejecutara.")
    verify_selected(device, disk_id)
    return stage, settings, disko


def install(device, disk_id, stage, settings, disko):
    print("\nResumen: UEFI · EFI 1 GiB · LUKS2 + Btrfs · Niri + DMS")
    print(f"Disco: {disk_id}\nModelo: {device.get('model')}\nSerie: {device.get('serial')}")
    print("La instalacion necesita internet. Si falla una descarga tras formatear, el sistema anterior ya no estara.")
    login_password = password("Contraseña de tu usuario")
    print("El primer arranque usa una contraseña de recuperacion del disco.")
    print("Despues configuraremos Secure Boot y TPM para el desbloqueo automatico.")
    luks_password = password("Contraseña de recuperacion del disco (guardala en Proton Pass)")
    if not confirm_erase(disk_id):
        print("Cancelado. No se ha formateado el disco.")
        return
    verify_selected(device, disk_id)
    # Disko unmounts its target first. Recheck after downloads and prompts so it
    # cannot unmount another volume that appeared at /mnt during preparation.
    require_target_free()
    SECRET_DIR.mkdir(mode=0o700, exist_ok=False)
    key = SECRET_DIR / "luks.key"
    try:
        fd = os.open(key, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as stream:
            stream.write(luks_password)
        del luks_password
        run([disko])
    finally:
        key.unlink(missing_ok=True)
        SECRET_DIR.rmdir()
    target = MOUNT / "etc/nixos"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(stage, target)
    run(["nixos-install", "--root", str(MOUNT), "--flake", f"path:{target}#elitebook",
         "--no-root-passwd", "--no-channel-copy", "--option", "experimental-features",
         "nix-command flakes", *CACHE_OPTIONS])
    run(["nixos-enter", "--root", str(MOUNT), "-c", "chpasswd"],
        input=f"{settings['username']}:{login_password}\n")
    del login_password
    user = settings["username"]
    uid = int(run(["nixos-enter", "--root", str(MOUNT), "-c", f"id -u {user}"], True))
    gid = int(run(["nixos-enter", "--root", str(MOUNT), "-c", f"id -g {user}"], True))
    home = MOUNT / "home" / user
    home.mkdir(parents=True, exist_ok=True)
    repo = home / "Sistema"
    shutil.copytree(stage, repo)
    run(["git", "-C", str(repo), "init", "-b", "main"])
    run(["git", "-C", str(repo), "add", "."])
    run(["git", "-C", str(repo), "-c", "user.name=Instalador", "-c",
         "user.email=installer@localhost", "commit", "-m", "Configuracion inicial del portatil"])
    os.chown(home, uid, gid)
    for path in [repo, *repo.rglob("*")]:
        os.chown(path, uid, gid)
    run(["sync"])
    print("\nINSTALACION COMPLETADA. Retira el USB al reiniciar.")
    print("Desbloquea el disco, inicia sesion y abre 'Primeros pasos' en el lanzador.")
    print("Para terminar el arranque automatico: lee docs/TPM-SECURE-BOOT.md en ~/Sistema.")
    print("Abre Pi y configura tu proveedor de nube antes de empezar a usar el agente.")
    print("No se reinicia automaticamente. Cuando estes listo: reboot")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--inspect", action="store_true")
    modes.add_argument("--install", action="store_true")
    args = parser.parse_args()
    devices = disk_inventory()
    describe(devices)
    if args.inspect:
        return
    require_live_environment()
    if not sys.stdin.isatty():
        raise RuntimeError("Hace falta una terminal interactiva. No se acepta instalacion desatendida.")
    lock_fd = os.open("/run/personal-os-installer.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        choice = input("\nNumero de disco (vacio cancela): ").strip()
        if not choice:
            return
        if not choice.isdigit() or not 1 <= int(choice) <= len(devices):
            raise RuntimeError("Seleccion no valida.")
        device = devices[int(choice) - 1]
        reason = rejection(device)
        if reason:
            raise RuntimeError("No se permite seleccionar ese disco: " + reason)
        disk_id = stable_path(device)
        verify_selected(device, disk_id)
        stage, settings, disko = prepare(device, disk_id)
        install(device, disk_id, stage, settings, disko)
    finally:
        os.close(lock_fd)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nInterrumpido. No reinicies si el formateo ya habia comenzado.", file=sys.stderr)
        sys.exit(130)
    except Exception as error:
        print(f"\nERROR: {error}", file=sys.stderr)
        print("El instalador se ha detenido. Si ya empezo el formateo, conserva esta sesion live para reparar.", file=sys.stderr)
        sys.exit(1)
