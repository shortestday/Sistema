# Included in a writeShellApplication wrapper (bash, strict mode).
action="${1:-help}"
if (( $# )); then shift; fi
repo="$HOME/Sistema"
case "$action" in
  pi) exec pi "$@" ;;
  lab) exec firefox --no-remote --profile "$HOME/.mozilla/firefox-lab" "$@" ;;
  study)
    cd "$HOME/Estudio" || exit 1
    exec pi "$@"
    ;;
  system)
    cd "$repo" || exit 1
    exec pi "$@"
    ;;
  check|apply)
    [[ -f "$repo/flake.lock" ]] || { echo 'No encuentro ~/Sistema/flake.lock'; exit 1; }
    nix flake check "path:$repo" --no-update-lock-file
    nix build "path:$repo#nixosConfigurations.elitebook.config.system.build.toplevel" --no-link --no-update-lock-file
    if [[ "$action" == apply ]]; then
      git -C "$repo" diff --stat
      read -r -p 'Aplicar esta configuracion? Escribe APLICAR: ' answer
      [[ "$answer" == APLICAR ]] || exit 1
      sudo nixos-rebuild switch --flake "path:$repo#elitebook" --no-update-lock-file
    fi
    ;;
  doctor)
    printf 'Escritorio: %s\n' "${XDG_CURRENT_DESKTOP:-sin sesion grafica}"
    for app in niri dms ghostty pi orca-ide zcode brave firefox burpsuite; do
      if command -v "$app" >/dev/null; then printf 'OK  %s\n' "$app"; else printf 'FALTA %s\n' "$app"; fi
    done
    systemctl --user --no-pager --full status dms.service || true
    ;;
  capture-desktop)
    source_file="$HOME/.config/DankMaterialShell/settings.json"
    jq empty "$source_file"
    cp "$source_file" "$repo/desktop/dms.json"
    printf 'Preferencias de DMS copiadas a ~/Sistema/desktop/dms.json. Revisa y guarda el cambio en Git.\n'
    ;;
  welcome)
    cat "$repo/docs/PRIMER-ARRANQUE.md"
    printf '\n'
    read -r -p 'Pulsa Intro para cerrar.' _answer
    ;;
  *)
    cat <<'HELP'
desk pi                Pi con el modelo que hayas seleccionado
desk study             Retomar la carpeta de estudio
desk system            Configurar tu sistema conversando con Pi
desk lab               Firefox con perfil separado
desk check             Validar y construir cambios sin activarlos
desk apply             Validar, construir y aplicar con confirmacion
desk capture-desktop   Guardar tus preferencias actuales de DMS en el repositorio
desk doctor            Comprobar aplicaciones y shell
desk welcome           Primeros pasos
HELP
    ;;
esac
