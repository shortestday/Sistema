#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ "${1:-}" == --help || $# == 0 ]]; then
  printf 'Uso: bash install.sh --inspect | --install\n\n--inspect: solo muestra discos; no instala ni formatea.\n--install: asistente para instalar NixOS borrando UN disco interno.\n'
  exit 0
fi
[[ $# == 1 && ( "$1" == --inspect || "$1" == --install ) ]] || { echo 'Argumento no reconocido.'; exit 2; }
if [[ $EUID != 0 ]]; then
  exec sudo bash "$PWD/install.sh" "$@"
fi
command -v nix >/dev/null || { echo 'Arranca primero desde el USB oficial de NixOS.'; exit 1; }
[[ -f flake.lock ]] || { echo 'Falta flake.lock. Usa el paquete completo, sin actualizar sus versiones.'; exit 1; }
exec nix --extra-experimental-features 'nix-command flakes' shell \
  "path:$PWD#installer-tools" --no-update-lock-file \
  -c python3 "$PWD/installer/install.py" "$@"
