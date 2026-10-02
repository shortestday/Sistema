# Diario del sistema

Registro humano de cambios, decisiones y estado del portátil. No guardar aquí secretos,
contraseñas, tokens, claves privadas ni datos sensibles.

## 2026-10-02

### Actualización del sistema y herramientas de archivos

- Actualizado `flake.lock` para traer versiones recientes de `nixpkgs`, Home Manager y `llm-agents.nix`.
- Aplicado el sistema actualizado; comprobado activo `26.05.20260930.78e9c78`.
- Firefox quedó en `157.0`, Pi en `1.0.0` y Orca en `1.4.218`.
- Añadido Yazi como explorador de archivos por terminal. Comprobado `yazi 26.5.6` activo.
- Commit realizado: `9afa54a Actualizar sistema y añadir Yazi`.

### Fondos, imágenes y exploración visual

- Generada selección de fondos cyberpunk/pixel-art/synthwave/Japón desde Wallhaven.
- Primero se dejaron miniaturas en `~/Pictures/Wallpapers/candidatos-4k`; después se descargaron los fondos completos en `~/Pictures/Wallpapers/4k-full`.
- La descarga completa contiene 40 imágenes 4K/5K/8K, unos 157 MiB, fuera del repo Git.
- Añadido Loupe como visor de imágenes dedicado.
- Declaradas asociaciones MIME para abrir PNG/JPEG/WEBP/GIF/AVIF/BMP/TIFF/SVG con Loupe en vez de Brave.

### Brave, Proton Pass y Firefox Lab

- Añadida instalación declarativa de la extensión Proton Pass en Brave mediante política `ExtensionInstallForcelist`.
- Recordatorio: la aplicación Proton Pass instalada no da autocompletado web por sí sola; el autocompletado depende de la extensión del navegador.
- Revisada la documentación/opciones oficiales de NixOS para `programs.firefox.policies`.
- Añadida instalación declarativa de FoxyProxy Standard en Firefox mediante `ExtensionSettings`.
- Se mantiene Firefox Lab como navegador separado para pruebas/Burp.

### Burp Suite y FoxyProxy

- Preparada configuración importable de FoxyProxy para Burp en `docs/foxyproxy-burp.json`.
- Burp escucha correctamente en `127.0.0.1:8080`.
- Importado el certificado CA de Burp en el perfil Firefox Lab (`~/.mozilla/firefox-lab`) con confianza TLS.
- Añadidos comandos:
  - `desk burp` para lanzar Burp Suite.
  - `desk burp-cert` para importar/reimportar el certificado CA de Burp en Firefox Lab, con Burp abierto.
- Añadido lanzador de escritorio `Burp Suite`.
- Burp empaquetado por NixOS observado en versión `2026.4.3`; avisó de que JRE `21.0.12` no está “fully tested”. Se consideró seguro continuar mientras no haya fallos reales.
- Burp avisó de actualización a `2026.8`; decisión: no actualizar desde el instalador interno, sino mediante Nix/`flake.lock`.
- Existe un instalador descargado en `~/Downloads/burpsuite_linux_v2026_8.sh`; no ejecutarlo. Valorar borrarlo.
- Comentada la alternativa OWASP ZAP: proxy/interceptor libre con scanner activo. Decisión actual: seguir con Burp Community; no instalar Caido ni ZAP por ahora.

### Chuleta del sistema

- Creada `docs/CHULETA.md` con atajos básicos de Niri/DMS, escritorios, archivos, Yazi, fondos, comandos `desk`, Brave/Proton y Burp.
- Añadido comando `desk chuleta` y lanzador `Chuleta del sistema`.
- Actualizada la ayuda de `desk` con los nuevos comandos.

### Validación

- Ejecutado `desk check` tras los cambios de Loupe, Proton Pass, Firefox/FoxyProxy, chuleta y Burp.
- Resultado: validación y construcción correctas.
- Pendiente tras aplicar: reiniciar Firefox Lab para que use el certificado importado y comprobar navegación HTTPS con FoxyProxy activo.

### Mantenimiento NixOS y diagnóstico

- Activado `services.btrfs.autoScrub.enable` para scrubs periódicos del Btrfs; timer observado para el día 1 de cada mes.
- Desactivada la edición interactiva de entradas de systemd-boot: `boot.loader.systemd-boot.editor = false`.
- Mejorado `desk check/apply` para mostrar diferencias entre generaciones con `nvd`.
- Cambiada la confirmación de `desk apply`: ahora pide un PIN numérico aleatorio de 4 cifras en vez de escribir `APLICAR`.
- Añadido `programs.nix-index.enable` para localizar paquetes que proporcionan comandos/archivos.
- Añadidas herramientas pequeñas de diagnóstico: `usbutils`, `pciutils`, `lm_sensors`, `vulkan-tools`, `clinfo` y `powertop`.
- Queda pendiente diseñar backups con Restic; un mini NAS de 2 bahías sería buen destino, recordando que RAID no sustituye backups versionados.

## 2026-10-01 (pendientes para mañana)

### GitHub y correo para Git

- Configurar identidad global de Git: `git config --global user.name` y `user.email` (ahora hay una local en este repo: `laotse <laotse@tao>`; el primer commit del instalador quedó como `Installer <installer@localhost>`).
- Crear repositorio remoto en GitHub y añadirlo: `git remote add origin git@github.com:USUARIO/Sistema.git`.
- Decidir visibilidad: el repo no contiene secretos, pero es preferible privado al principio.
- Para empujar por SSH hará falta clave SSH en la cuenta de GitHub (ya existe `~/.ssh/id_ed25519_tao` de tao; valorar generar una clave dedicada para GitHub).
- Primer push: `git push -u origin main`.

### Copias de seguridad con Restic

- Restic ya está instalado en tao; falta decidir y configurar destino, frecuencia y prueba de restauración.
- Destino propuesto: hermes por SSH (ya hay acceso por clave) u otro disco; decidir con el usuario.
- Qué respaldar: ~/Documentos, ~/Estudio, ~/Sistema y configs de aplicaciones que interesen.
- Planear: inicializar repo restic, contraseña (guardarla fuera del equipo, ej. Proton Pass), programación (systemd timer) y restauración de prueba real.

### Qué se sube a GitHub (aclaración)

- Solo archivos de configuración: flake.nix, flake.lock, modules/, desktop/, scripts/, docs/, host/.
- Tamaño actual del repo: ~536 KB (34 archivos). El histórico Git: ~340 KB.
- Los programas no van en el repo: Nix los descarga de cache.nixos.org según los hashes de flake.lock al aplicar en otra máquina.
- Nunca subir: auth.json, claves SSH, tokens, contraseñas ni llaveros (viven fuera del repo, en ~/.pi, ~/.ssh, etc.).
- Los rollbacks de NixOS no recuperan documentos ni datos de aplicaciones; GitHub solo replica la configuración del sistema.

## 2026-09-30

### SSH

- Preparada la activación de SSH entrante en `modules/system.nix`.
- Servicio: `services.openssh.enable = true`.
- Firewall: puerto SSH abierto mediante `openFirewall = true`.
- Autenticación por contraseña permitida provisionalmente.
- Login de `root` por SSH desactivado.
- IP local observada para conexión en la red actual: `192.168.1.137`.
- Comando previsto desde otro equipo:

```bash
ssh laotse@192.168.1.137
```

### Pi

- Preparada actualización del input `llm-agents` en `flake.lock`.
- Versión anterior de Pi observada: `0.87.1`.
- Versión que aparece en el nuevo build validado: `0.99.1`.
- Revisada configuración de Pi en `hermes` sin leer `auth.json` ni mostrar claves/API tokens.
- Añadido en `tao` `~/.pi/agent/models.json` con proveedor `local-glm` hacia `http://dgx2:8888/v1` y modelo elegible `GLM-5.3-Flash-EXL3`.
- Validado con `pi --offline --list-models GLM` y una prueba mínima sin herramientas: respuesta `OK` usando `local-glm/GLM-5.3-Flash-EXL3`.

### Shell

- Shell inicial del usuario: Bash.
- Preparado Fish como shell de login en `modules/system.nix`:

```nix
programs.fish.enable = true;
users.users.${host.username}.shell = pkgs.fish;
```

- Bash sigue disponible para scripts y uso manual.

### Validación

- Ejecutado `desk check` después de preparar SSH, actualización de Pi y Fish.
- Resultado: validación y construcción correctas.

### Aplicación

- Cambios aplicados con `desk apply`.
- Correcciones DMS/Niri aplicadas después: DMS corre con `dms-shell-personal-1.4.6`, Home Manager activó correctamente y `~/.config/niri/dms/binds.kdl` quedó inicializado.
- Comprobación visual del usuario: Ajustes DMS muestra barra lateral/desplazamiento para acceder a opciones inferiores.
- Alias Fish `aplicar-sistema` comprobado en sesión interactiva.
- `desk doctor` confirma presentes Niri, DMS, Ghostty, Pi, Orca, Z Code, Brave, Firefox y Burp.
- Comprobado `niri validate -c ~/.config/niri/config.kdl`: configuración real de Niri válida.
- Comprobadas políticas Brave declaradas: Rewards y News desactivados.
- Comprobado perfil Firefox Lab separado con `user.js` inicial.
- Mejorado `desk doctor` para mostrar versiones básicas, validación real de Niri, estado de Home Manager y estado de DMS.
- Revisado endurecimiento SSH: no existe `~/.ssh/authorized_keys`, así que no se desactiva autenticación por contraseña todavía para no bloquear acceso remoto por clave.

### Ajustes de uso del escritorio

- Activado auto-ocultado de la barra superior de DMS en la configuración viva y en `desktop/dms.json` para futuras sesiones/instalaciones.
- Copia previa de ajustes DMS: `~/.config/DankMaterialShell/settings.json.before-autohide-20260930180356`.
- Cambiado Niri para que las ventanas nuevas usen ancho completo por defecto: `default-column-width { proportion 1.0; }`.
- Se conservan los anchos predefinidos 50%, 66% y 100%, alternables con `Super+R`.

### SSH con Hermes

- Detectado `hermes` accesible en la red local: `192.168.1.136`.
- Preparada clave SSH local de `tao`: `~/.ssh/id_ed25519_tao`.
- Añadido alias local en `~/.ssh/config`: `Host hermes`, usuario `narkha`, clave `id_ed25519_tao`.
- Clave pública de `tao` autorizada en `hermes`.
- Comprobado acceso por clave: `ssh hermes` entra como `narkha@hermes` sin contraseña.

### Tailscale, Proton Pass y Orca/Hermes

- Preparada instalación declarativa de Tailscale en `tao`: `services.tailscale.enable = true` y CLI `tailscale`.
- Preparada instalación de Proton Pass oficial desde nixpkgs fijado: `proton-pass` 1.36.1 y `proton-pass-cli` 2.0.2; su binario CLI expuesto es `pass-cli`.
- Mejorado `desk doctor` para comprobar `proton-pass`, `pass-cli`, `tailscale`, `tailscaled.service` y `tailscale status`.
- Observado en `hermes`: Tailscale ya activo y conectado, IP tailnet `100.126.22.47`.
- Observado en `hermes`: Orca disponible como `orca-ide`; el comando `orca` no existe allí, pero `orca-ide serve` sí.
- `tao` unido a Tailscale con IP tailnet `100.125.138.9`; `hermes` aparece activo/directo.
- Emparejado Orca en `tao` con Orca Server de `hermes` sin mostrar el pairing code: `orca environment list` muestra `hermes  ws://100.126.22.47:6768`.
- Pendiente: iniciar sesión en Proton Pass por GUI o `pass-cli login` si el usuario quiere usar la CLI.
- `pass-cli login` falló inicialmente con `AccessDenied` al acceder al keyring. Diagnóstico: `services.gnome.gnome-keyring.enable = true`, pero `security.pam.services.sddm.enableGnomeKeyring` estaba desactivado.
- Preparada integración PAM de GNOME Keyring en SDDM y añadido `libsecret`/`secret-tool` para diagnóstico del Secret Service. Requiere aplicar y cerrar sesión/reiniciar sesión para que el llavero se desbloquee al login.
- Tras el cambio, `pass-cli login` volvió a fallar en la sesión antigua; diagnóstico: la configuración declarativa ya evalúa `sddm.enableGnomeKeyring = true`, pero el `gnome-keyring-daemon` de la sesión actual nació antes del cambio. Pendiente reiniciar o cerrar sesión y volver a entrar antes de repetir la prueba.
- Proton Pass en navegadores: para autocompletar contraseñas se usará la extensión oficial en Brave. En Firefox Lab solo instalarla si hace falta, por ser navegador de laboratorio/Burp.
- SSH comprobado activo con `systemctl status sshd`.
- Pi comprobado en versión `0.99.1`.
- Fish comprobado en versión `4.7.1`.
- Fish queda como shell de login por defecto para el usuario `laotse`.
- Comprobado después: las terminales nuevas abren Fish correctamente como shell de login.
- Añadido alias declarativo de Fish `aplicar-sistema` para ejecutar `cd ~/Sistema && desk apply`.
- Detectado que Home Manager no pudo activar el alias porque existía un `~/.config/fish/config.fish` manual mínimo; preparada copia automática con extensión `.hm-backup`.
- Ajustado el seed para rellenar `~/.config/niri/dms/binds.kdl` si falta o está vacío, sin pisarlo si contiene atajos.

### Proton Pass: diagnóstico y arreglo de pass-cli

- Síntoma: `pass-cli test/login` fallaba con `Could not get local key from keyring: NoStorageAccess(AccessDenied)`.
- El Secret Service de GNOME Keyring funciona (probado con `secret-tool`); el problema no era el PAM.
- pass-cli usa el llavero del kernel (keyutils). La clave `keyring:cli-local-key:...@ProtonPassCLI` estaba en el keyring de sesión con permisos restrictivos para el usuario (solo `view`), y pass-cli no podía buscarla ni releerla.
- Diagnóstico con `strace`: `KEYCTL_SEARCH` sobre el keyring de sesión devolvía `EACCES` pese a que la clave existía y era legible por posesión.
- Arreglo aplicado: `keyctl setperm <id> 0x3f3f0000` (poseedor y usuario con todos los permisos; grupo/otros sin acceso) sobre la clave local.
- Tras el arreglo, `pass-cli test` supera la etapa del keyring y solo queda la autenticación pendiente.
- Comprobado `desk doctor` tras aplicar la última generación: 12 aplicaciones OK, Niri válido, Home Manager y DMS activos, Tailscale conectado con `hermes` y `dgx2` visibles. El desbloqueo de pantalla desbloquea el llavero (`gkr-pam: unlocked login keyring`).
- `pass-cli login` completado por el usuario con éxito tras el arreglo.
- Nota: el llavero del kernel es volátil; si tras reiniciar vuelve el `AccessDenied`, repetir el `setperm` sobre la clave nueva y valorar alternativa duradera.

### Pendiente tras reinicio o nueva sesión

- Tras reiniciar, comprobar `pass-cli test`; si vuelve el `AccessDenied`, aplicar `keyctl setperm <id> 0x3f3f0000` sobre la clave nueva.
- Instalar/iniciar sesión en la extensión Proton Pass de Brave para autocompletar contraseñas.
- Probar `desk doctor` después de aplicar la última generación.
- Comprobar visualmente que la barra DMS se auto-oculta y aparece al acercar el ratón arriba.
- Comprobar que Brave/Ghostty nuevos abren a ancho completo con Niri.
- Si SSH queda estable por claves, valorar desactivar `PasswordAuthentication` en `modules/system.nix`.
- Cuando el estado sea bueno, hacer commit del repo.

### Estado del repositorio

- Cambios pendientes de commit:
  - `README.md`
  - `desktop/dms.json`
  - `desktop/dms-es.json`
  - `desktop/niri.kdl`
  - `docs/DIARIO.md`
  - `docs/GUI-CORRECTIONS.md`
  - `flake.lock`
  - `modules/home.nix`
  - `modules/system.nix`
  - `packages/dms-personal.nix`
  - `scripts/desk.sh`
  - `scripts/patch-dms.py`
  - `scripts/seed.py`
