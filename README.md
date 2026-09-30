# Instalador del portatil personal

NixOS + Niri + DankMaterialShell. Terminal primero, escritorio completo y discreto.
Incluye Ghostty, Pi, Orca, Z Code, Brave, Firefox Lab, Burp Community, herramientas
de terminal/acceso remoto y OpenVPN/WireGuard. Brave lleva News y Rewards
desactivados. Pi queda preparado para configurar tu proveedor de nube.

## Alcance de esta version

Instalacion **de disco completo**, x86_64, UEFI, un disco interno de al menos 64 GiB.
EFI 1 GiB + LUKS2 + Btrfs con subvolumenes root/home/nix. Zram; sin hibernacion.
No implementa dual boot ni migracion de datos. No instala KDE ni GNOME Shell.
El greeter SDDM y algunas aplicaciones GTK no añaden otra sesion de escritorio.

La descarga inicial requiere internet. Los agentes de nube necesitan que configures
tu proveedor e inicies sesion; no se incluyen claves. La IA local queda aplazada.

## Preparacion del USB

1. Haz copia de los archivos del HP y comprueba que puedes abrir esa copia.
2. Descarga una ISO oficial **NixOS 26.05 x86_64** de https://nixos.org/download/.
   La ISO grafica facilita conectarte a Wi-Fi; su escritorio live no determina el instalado.
3. Graba la ISO con balenaEtcher. Se borra el USB elegido, no el disco interno.
4. Conserva este paquete en **otro USB** o en una ubicacion accesible desde el live.
   Etcher graba una imagen de solo lectura: no basta con copiar este ZIP al mismo USB.
   Tambien puedes alojar tu copia del repositorio y clonarla en el entorno live.
5. Arranca el HP desde el USB en modo UEFI. Si el medio no arranca con Secure Boot,
   revisa su configuracion; este paquete no provisiona claves Secure Boot.

## Ejecutar

Abre una terminal en la carpeta extraida `nixos-personal`:

```bash
bash install.sh --inspect
```

Solo enumera discos. Para iniciar el asistente:

```bash
bash install.sh --install
```

El asistente pide el disco, usuario, nombre, teclado, idioma y zona horaria. Captura
la configuracion del hardware; evalua el sistema y comprueba el plan de descargas
con las versiones fijadas. No selecciona un disco por defecto. Rechaza USB,
unidades extraibles, discos montados y dispositivos LUKS/LVM/RAID abiertos.

Antes de borrar pide contraseñas de usuario y cifrado y exige escribir literalmente
`BORRAR /dev/disk/by-id/...` con el identificador mostrado. Si no quieres borrar
TODO ese disco, cancela. No hay una opcion de aceptar automaticamente.

Tras la confirmacion formatea e instala. Necesita descargar paquetes: un fallo de
red en esa fase puede dejar una instalacion incompleta y el sistema anterior ya borrado.
No se promete una instalacion transaccional ni la recuperacion del sistema anterior.
Los inicios de sesion se completan despues del primer arranque.

## Despues

Abre **Primeros pasos** en DMS. Lee [la guia de primer arranque](docs/PRIMER-ARRANQUE.md).
La configuracion queda en `~/Sistema`, con un primer commit Git. `/etc/nixos` conserva
una copia de la instalacion; los cambios diarios se hacen en `~/Sistema`.

El primer arranque solicita la contraseña del disco. Para activar el desbloqueo
automatico con TPM y Secure Boot, sigue [esta guia](docs/TPM-SECURE-BOOT.md).
La contraseña se conserva como recuperacion; no se registra el TPM desde el USB.

Niri y Ghostty se gestionan con Home Manager. DMS y Pi reciben valores iniciales
editables; el seed no pisa ajustes o sesiones. Cambiar los valores iniciales del
repositorio no modifica automaticamente los archivos editables que ya existan.
`desk capture-desktop` recoge tus ajustes DMS para la siguiente instalacion.

## Validacion y limites

Consulta [VALIDACION.md](VALIDACION.md) para distinguir lo probado de lo pendiente.
El instalador siempre vuelve a evaluar la configuracion del hardware real antes de borrar.
No se ha ejecutado aqui ninguna operacion sobre el disco del HP.

Para comprobar sin instalar desde un equipo Linux con Nix:

```bash
python3 -m unittest discover -s tests -v
nix flake check --no-update-lock-file
nix eval .#nixosConfigurations.elitebook.config.system.build.toplevel.drvPath --raw
nix build .#nixosConfigurations.elitebook.config.system.build.toplevel --dry-run --no-link
```

`host/settings.json` contiene un disco marcador y `host/hardware.nix` una plantilla
solo para evaluacion. El asistente sustituye ambos en una copia temporal. No ejecutes
Disko directamente contra esta plantilla ni inventes el identificador del HP.

## Reproducibilidad y mantenimiento

- `flake.lock` fija las fuentes de NixOS, Home Manager, Disko, Lanzaboote y llm-agents.nix.
- Los paquetes de Pi/Orca/Z Code proceden de numtide/llm-agents.nix, mantenido por terceros.
- Versiones fijadas no garantizan que sus descargas sigan disponibles para siempre.
- No hay actualizaciones automaticas ni borrado automatico de generaciones.
- Restic esta instalado; destino, frecuencia y prueba de restauracion siguen pendientes.
- SSH entrante está habilitado provisionalmente para administración local; root no puede entrar por SSH. Los agentes no se ejecutan como root.
- Los agentes utilizan el proveedor de nube que configures y necesitan conexion.

## Fuentes tecnicas

- https://nixos.org/manual/nixos/stable/
- https://github.com/nix-community/disko
- https://github.com/nix-community/home-manager
- https://danklinux.com/docs/dankmaterialshell/nixos
- https://github.com/niri-wm/niri
- https://github.com/numtide/llm-agents.nix
- https://pi.dev/docs/latest/models
- https://support.brave.app/hc/en-us/articles/360039248271-Group-Policy

Revisa cambios y fuentes antes de ejecutar software con privilegios de administrador.
