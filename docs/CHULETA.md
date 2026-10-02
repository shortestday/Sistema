# Chuleta rapida del sistema

## Teclas principales

- `Super + Return`: abrir terminal Ghostty.
- `Super + Space`: buscador de aplicaciones / spotlight.
- `Super + E`: abrir Archivos.
- `Super + P`: abrir Pi.
- `Super + B`: abrir Brave.
- `Super + ,`: ajustes del shell.
- `Super + Shift + L`: bloquear pantalla.
- `Super + Shift + /`: ver todos los atajos.

`Super` es la tecla Windows.

## Ventanas y escritorios

- `Super + O`: vista general.
- `Super + Q`: cerrar ventana.
- `Super + F`: maximizar columna.
- `Super + Shift + F`: pantalla completa.
- `Super + R`: cambiar ancho de columna.
- `Super + V`: ventana flotante.
- `Super + Flechas`: moverse entre ventanas/columnas.
- `Super + Shift + Flechas`: mover ventanas/columnas.
- `Super + PageUp/PageDown`: escritorio anterior/siguiente.
- `Super + Shift + PageUp/PageDown`: mover ventana a otro escritorio.
- `Super + 1`, `Super + 2`, `Super + 3`: ir a escritorios 1, 2 y 3.

## Archivos

- GUI: `Super + E` abre Nautilus.
- Terminal: `yazi` abre el explorador TUI.
- Carpeta concreta: `yazi ~/Pictures/Wallpapers/4k-full`.
- Buscar archivos: `fd texto`.
- Buscar dentro de archivos: `rg texto`.

## Imagenes y fondos

- Visor de imagenes: Loupe.
- Fondos 4K descargados: `~/Pictures/Wallpapers/4k-full`.
- Candidatos/galeria: `~/Pictures/Wallpapers/candidatos-4k/index.html`.

## Sistema

Desde `~/Sistema`:

- Validar cambios: `desk check`.
- Aplicar cambios: `desk apply`.
- Diagnostico rapido: `desk doctor`.
- Abrir esta chuleta: `desk chuleta`.
- Configurar con Pi: `desk system`.

## Navegador, claves y Burp

- Brave es el navegador diario.
- Firefox Lab va separado con `desk lab`.
- Proton Pass esta instalado; el autocompletado web lo da la extension de Brave.
- FoxyProxy se instala en Firefox para usarlo con Burp Suite.
- Config Burp para FoxyProxy: `~/Sistema/docs/foxyproxy-burp.json`.
- Lanzar Burp: `desk burp` o buscador -> `Burp Suite`.
- En FoxyProxy: Options -> Import -> elige ese JSON -> activa `Burp Suite` cuando Burp escuche en `127.0.0.1:8080`.
- Certificado HTTPS de Burp en Firefox Lab: `desk burp-cert` con Burp abierto. Reinicia Firefox Lab si estaba abierto.
- No ejecutes instaladores de Burp descargados; Burp se actualiza con Nix (`flake.lock` + `desk apply`).
