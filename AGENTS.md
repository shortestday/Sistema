# Tu sistema personal

Este repositorio es la fuente de verdad del portatil de Raul. Lee README.md y
host/settings.json antes de cambiarlo. Habla en español y explica cambios concretos.

## Decisiones

- NixOS, Niri y DankMaterialShell; una sola sesion. No añadir KDE, GNOME Shell ni Hyprland.
- Terminal primero, GUI disponible; escritorio limpio y personalizacion moderada.
- Pi centro de control; Orca instalado; Z Code para estudiar si el usuario lo elige.
- Brave diario; Firefox Lab separado; Burp Community. No Caido.
- Laboratorios y cargas grandes en otras maquinas. No instalar contenedores ni montar labs aqui por iniciativa propia.
- IA mediante proveedores de nube elegidos por el usuario. La IA local queda aplazada; no añadir motores ni descargar modelos por iniciativa propia.

## Donde cambiar cosas

- modules/system.nix: servicios y aplicaciones.
- modules/home.nix: preferencias declarativas, terminal y lanzadores.
- desktop/niri.kdl: ventanas y atajos. Home Manager lo enlaza; edita el original aqui.
- desktop/dms.json: ajustes iniciales de DMS. DMS escribe en ~/.config/DankMaterialShell/settings.json.
  Para cambiar la sesion actual modifica ese JSON con DMS cerrado y vuelve a arrancarlo;
  conserva campos desconocidos. desk capture-desktop guarda el resultado en este repo.
  El seed no pisa ajustes existentes; editar solo el JSON del repo no cambia una sesion ya creada.
- host/settings.json: usuario, idioma, teclado, equipo y disco.
- host/hardware.nix: generado en el equipo; conserva informacion de hardware.
- scripts/: acciones manuales y del agente mediante la misma interfaz desk.

## Ciclo de cambios

1. Comprueba git status y respeta los cambios pendientes del usuario.
2. Consulta las opciones de las versiones fijadas en flake.lock.
3. Haz el cambio minimo y explica su efecto.
4. Ejecuta desk check. No afirmes que funciona si no se ha validado.
5. desk apply solicita confirmacion y sudo para activar el cambio.
6. Comprueba el resultado real y registra los cambios en Git cuando se solicite.

No ejecutes el instalador, Disko, mkfs, wipefs, cambios de particiones o borrados por
una peticion de personalizar el escritorio. No añadas sudo sin contraseña ni trusted-users.
No ejecutes el agente como root. Las instrucciones son orientacion, no un sandbox.
No leas ni registres tokens, auth.json, contraseñas o claves privadas.
No hagas nix flake update de forma incidental. Las actualizaciones se deciden aparte.
Los rollbacks de NixOS no recuperan documentos ni datos de aplicaciones.

## Conexion

Pi usa el proveedor y modelo de nube que configure el usuario. Los agentes necesitan
conexion para responder. El escritorio, la terminal y los documentos locales siguen
disponibles sin red.
