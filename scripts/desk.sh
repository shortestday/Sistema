# Included in a writeShellApplication wrapper (bash, strict mode).
action="${1:-help}"
if (( $# )); then shift; fi
repo="$HOME/Sistema"
case "$action" in
  pi) exec pi "$@" ;;
  lab) exec firefox --no-remote --profile "$HOME/.mozilla/firefox-lab" "$@" ;;
  burp) exec burpsuite "$@" ;;
  burp-cert)
    profile="$HOME/.mozilla/firefox-lab"
    [[ -d "$profile" ]] || { echo "No encuentro el perfil Firefox Lab: $profile"; exit 1; }
    tmp_cert=$(mktemp)
    trap 'rm -f "$tmp_cert"' EXIT
    curl -fsS --proxy http://127.0.0.1:8080 --max-time 10 -o "$tmp_cert" http://burp/cert || {
      echo 'No puedo descargar el certificado desde Burp. Abre Burp y comprueba que escucha en 127.0.0.1:8080.'
      exit 1
    }
    certutil -D -d "sql:$profile" -n 'PortSwigger Burp Suite CA' >/dev/null 2>&1 || true
    certutil -A -d "sql:$profile" -n 'PortSwigger Burp Suite CA' -t 'C,,' -i "$tmp_cert"
    echo 'Certificado CA de Burp importado en Firefox Lab. Reinicia Firefox Lab si estaba abierto.'
    ;;
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
    pretty_name=$(grep '^PRETTY_NAME=' /etc/os-release | cut -d= -f2- | tr -d '"')
    printf 'Sistema: %s\n' "$pretty_name"
    printf 'Kernel: %s\n' "$(uname -r)"
    fish --version || true
    pi --version || true
    niri --version || true
    printf '\nAplicaciones:\n'
    for app in niri dms ghostty pi orca-ide zcode brave firefox burpsuite proton-pass pass-cli tailscale; do
      if command -v "$app" >/dev/null; then printf 'OK  %s\n' "$app"; else printf 'FALTA %s\n' "$app"; fi
    done
    printf '\nNiri config:\n'
    niri validate -c "$HOME/.config/niri/config.kdl" 2>&1 || true
    printf '\nHome Manager:\n'
    systemctl --no-pager --full status "home-manager-$USER.service" || true
    printf '\nDMS:\n'
    systemctl --user --no-pager --full status dms.service || true
    printf '\nTailscale:\n'
    systemctl --no-pager --full status tailscaled.service || true
    tailscale status || true
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
  chuleta)
    cat "$repo/docs/CHULETA.md"
    printf '\n'
    read -r -p 'Pulsa Intro para cerrar.' _answer
    ;;
  *)
    cat <<'HELP'
desk pi                Pi con el modelo que hayas seleccionado
desk study             Retomar la carpeta de estudio
desk system            Configurar tu sistema conversando con Pi
desk lab               Firefox con perfil separado
desk burp              Burp Suite
desk burp-cert         Importar certificado CA de Burp en Firefox Lab
desk check             Validar y construir cambios sin activarlos
desk apply             Validar, construir y aplicar con confirmacion
desk capture-desktop   Guardar tus preferencias actuales de DMS en el repositorio
desk doctor            Comprobar aplicaciones y shell
desk welcome           Primeros pasos
desk chuleta           Chuleta rapida de atajos y comandos
HELP
    ;;
esac
