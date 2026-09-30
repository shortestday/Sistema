# Validacion · 30 de septiembre de 2026

## Resultado

Paquete de instalacion creado y validado a nivel de configuracion y scripts.
**No se ha realizado una instalacion completa ni un arranque de este sistema**,
ni en una maquina virtual ni en el HP. No se ha modificado ningun disco del HP.
No es una ISO personalizada: se utiliza junto a la ISO oficial de NixOS.

Las comprobaciones se han ejecutado en Linux (Ubuntu sobre WSL), utilizando
Nix 2.20.6 portable y las fuentes exactas de `flake.lock`.

| Comprobacion | Resultado |
|---|---|
| Evaluar el sistema NixOS completo | Correcto, genera su derivacion |
| `nix flake check` | Correcto: configuracion y tres checks |
| `niri validate` con Niri 26.04 | Correcto |
| ShellCheck para install.sh y desk.sh | Correcto |
| 16 pruebas Python del instalador, preferencias y actualizacion TPM | Correcto |
| Construir el script Disko | Correcto; NO se ejecuta |
| Calcular el plan de construccion del sistema | Correcto; NO equivale a construirlo |
| Configuracion de arranque LUKS | keyFile=null; no incorpora la clave temporal |
| Configuracion Secure Boot + TPM | Evalua; Lanzaboote activo, systemd-boot desactivado, tpm2-device=auto |

Se ha añadido Lanzaboote 1.2.0 sin cambiar las revisiones ya fijadas. Secure Boot y
desbloqueo TPM permanecen desactivados por defecto hasta provisionar las claves en
el HP instalado. La evaluacion de esa variante no demuestra un arranque real ni
el registro de claves o TPM; esos pasos estan pendientes en el hardware.
La actualizacion del paquete anterior conserva host/settings.json y hardware.nix
y rechaza cambios propios en los archivos que sustituye.

Las pruebas Python usan discos y ejecuciones simulados. Comprueban el rechazo
de USB, unidades montadas, swap y dependencias abiertas; cambios de identidad o
montaje durante la preparacion; confirmacion exacta; cancelacion sin formateo;
limpieza de la clave si falla el particionado; destino ocupado durante la espera;
y conservacion de preferencias.
No sustituyen una prueba del flujo completo sobre hardware.

El volumen de descarga depende de la cache y de lo que ya tenga la ISO.
El asistente calcula el plan de paquetes antes de pedir confirmacion de borrado.
Deja margen de espacio y tiempo para las descargas y construcciones.

## Versiones fijadas

| Componente | Version evaluada |
|---|---|
| NixOS | 26.05, revision 7fc6f2c20af09cdcaf48b92ec3121860139ec668 |
| Niri | 26.04 |
| DankMaterialShell | 1.4.6 |
| Ghostty | 1.3.1 |
| Pi | 0.87.1 |
| Orca IDE | 1.4.216 |
| Z Code | 3.14.3 |
| Brave | 1.96.59 |
| Firefox | 156.0.1 |
| Burp Community | 2026.4.3 |

`flake.lock` contiene las revisiones y hashes completos. Los agentes usan el
proveedor de nube que configure el usuario; la IA local queda aplazada.

## Pendiente antes de dar el portatil por terminado

- Construccion e instalacion completas, arranque UEFI y desbloqueo LUKS.
- Registro Secure Boot/TPM y arranque automatico real; conservar la contraseña de recuperacion.
- Inicio de sesion, barra/lanzador DMS, ventanas y apertura de todas las apps.
- Wi-Fi, VPN HTB, Bluetooth, audio, microfono, brillo y touchpad.
- Bloqueo manual, cierre de tapa, suspension y desbloqueo al volver.
- Pantalla externa y compartir pantalla si vas a utilizarlos.
- Inicio de sesion en proveedores de nube; no se han utilizado credenciales.
- Probar respuestas y uso de herramientas con el proveedor de nube elegido.
- Elegir destino de copias y comprobar una restauracion de los apuntes.

Si una instalacion falla despues de confirmar el borrado, conserva la sesion live.
El asistente no tiene una opcion de reanudar automaticamente y rechazara `/mnt`
ocupado. No lo fuerces ni repitas Disko: primero revisa el error y los montajes.

## Repetir las comprobaciones

Desde esta carpeta, en Linux con Nix y flakes habilitados:

```bash
python3 -m unittest discover -s tests -v
nix flake check --no-update-lock-file
nix eval .#nixosConfigurations.elitebook.config.system.build.toplevel.drvPath --raw
nix build .#nixosConfigurations.elitebook.config.system.build.diskoScript --no-link
nix build .#nixosConfigurations.elitebook.config.system.build.toplevel --dry-run --no-link
```

Estos comandos no instalan el sistema. Construir el script Disko crea un archivo
en el almacen de Nix; ejecutarlo seria una operacion distinta y destructiva.
