# Disco cifrado y arranque automatico con TPM

Se configura en el HP instalado, despues del primer arranque. El USB live no
provisiona claves. Conserva la contraseña de disco en Proton Pass; el TPM no
sustituye esa via de recuperacion. El primer arranque pide esa contraseña.

## 1. Preparar el arranque firmado

Si instalaste con el paquete anterior, incorpora primero esta actualizacion con
`python3 update-tpm.py "$HOME/Sistema"` desde la carpeta del paquete nuevo.
No sustituye tu usuario, disco ni configuracion de hardware.

Desde el sistema instalado:

```bash
cd "$HOME/Sistema"
git status --short
sudo sbctl status
```

Si sbctl aun no esta disponible, construye y activa primero la configuracion
actualizada, manteniendo `secureBoot` y `tpmUnlock` en `false`:

```bash
sudo nixos-rebuild switch --flake "path:$HOME/Sistema#elitebook" --no-update-lock-file
```

Crea las claves solo si `sbctl status` indica que no estan instaladas:

```bash
sudo sbctl create-keys
```

Las claves privadas quedan en `/var/lib/sbctl`, fuera del repositorio. No las
copies a Git ni al almacen de Nix.

En `host/settings.json`, establece `"secureBoot": true` y deja
`"tpmUnlock": false`. Conserva el resto de los campos. Despues:

```bash
sudo nixos-rebuild boot --flake "path:$HOME/Sistema#elitebook" --no-update-lock-file
sudo sbctl verify
```

Comprueba que la nueva entrada Lanzaboote esta firmada. Pueden quedar archivos de
generaciones antiguas sin firmar; no actives Secure Boot si la entrada nueva falla.

## 2. Registrar las claves en el firmware HP

Este paso requiere mirar la pantalla real del firmware: no todos los HP usan
los mismos nombres. Entra con F10 y localiza Secure Boot y la gestion de claves.
Necesitamos Setup Mode para registrar nuestras claves. No limpies el TPM ni
borres indiscriminadamente las claves o la lista de revocacion dbx.

Tras poner el firmware en Setup Mode, vuelve a arrancar NixOS, aun con contraseña.
Comprueba `sudo sbctl status`. Solo si indica Setup Mode habilitado:

```bash
sudo sbctl enroll-keys --microsoft --firmware-builtin
```

Si falla, detente y conserva la salida para revisar; no fuerces el registro.
Reinicia, activa Secure Boot en el firmware y arranca la nueva entrada NixOS.
`sudo sbctl status` debe mostrar Secure Boot habilitado y Setup Mode deshabilitado.

## 3. Registrar el TPM, con Secure Boot ya activo

Comprueba otra vez Secure Boot y el dispositivo cifrado que realmente esta abierto:

```bash
sudo sbctl status
sudo cryptsetup status cryptroot
```

Copia la ruta mostrada en la linea `device:` del segundo comando. No uses
`/dev/mapper/cryptroot`: necesitamos su particion LUKS subyacente.

```bash
read -r -p 'Particion indicada en device: ' luks_device
sudo cryptsetup isLuks "$luks_device"
```

Continua solo si la ruta corresponde a la linea `device:` de cryptroot y la
comprobacion anterior tiene exito. Con Secure Boot habilitado:

```bash
sudo systemd-cryptenroll --tpm2-device=auto --tpm2-pcrs=7 --tpm2-with-pin=no "$luks_device"
```

Pide la contraseña de recuperacion del disco. No añadas `--wipe-slot`: conservamos
la contraseña. Si ya hay un registro TPM, revisalo antes de añadir otro.
PCR 7 vincula el desbloqueo a la politica de Secure Boot; no solicita PIN para
permitir el arranque desatendido.

Ahora establece `"tpmUnlock": true` en `host/settings.json`, manteniendo
`"secureBoot": true`, y ejecuta:

```bash
sudo nixos-rebuild boot --flake "path:$HOME/Sistema#elitebook" --no-update-lock-file
sudo sbctl verify
```

Reinicia y comprueba que llega al inicio de sesion sin pedir la contraseña del
disco. Solo ese arranque confirma el resultado. Si el TPM falla, usa la contraseña
de recuperacion; no repitas el instalador ni el particionado.

## Uso posterior

- SSH y Tailscale funcionan despues de desbloquear el sistema, cuando los configures.
- Secure Boot protege el arranque; al estar encendido, los datos estan accesibles
  para el sistema. Mantiene importancia el bloqueo de sesion.
- Cambiar claves de Secure Boot, firmware o TPM puede pedir la contraseña de recuperacion.
- No asegura WoL: se prueba aparte con el firmware, la tarjeta de red y la alimentacion.
- Protege la configuracion del firmware con contraseña si quieres dificultar que
  otra persona cambie la politica de arranque.

Fuentes: [Lanzaboote: preparacion](https://nix-community.github.io/lanzaboote/getting-started/prepare-your-system.html),
[registro de claves](https://nix-community.github.io/lanzaboote/getting-started/enable-secure-boot.html),
[cifrado en NixOS](https://wiki.nixos.org/wiki/Full_Disk_Encryption).
