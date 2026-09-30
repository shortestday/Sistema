# Primer arranque

1. Conecta la red desde la barra.
2. Abre Primeros pasos desde el lanzador (Super+Espacio).
3. Ejecuta `desk doctor` en una terminal para comprobar las aplicaciones.
4. Abre `desk pi` y configura tu proveedor de nube. Usa `/login` si admite ese
   inicio de sesion, o su clave API; despues selecciona el modelo con `/model`.
   Prueba una lectura de un archivo de ~/Estudio. Mantén las claves fuera de Git.
5. Inicia sesion en Orca y Z Code si vas a usarlos. No hay credenciales incluidas.
6. Brave: Rewards y News ya estan desactivados mediante tus politicas de NixOS.
   Compruebalas en `brave://policy`; "administrado" se refiere a esta configuracion
   local tuya. Oculta imagenes patrocinadas en nueva pestaña y activa bloqueo
   agresivo si lo prefieres. Shields viene con el navegador.
7. Para PortSwigger abre Burp Community y su navegador integrado. Firefox Lab
   tiene perfil separado; proxy y certificado se configuran cuando los necesites.
   Los proyectos persistentes y el scanner de Burp Pro no estan incluidos.
8. Abre ~/Estudio desde tu agente preferido. Cada materia tiene PROGRESO.md.

## Conectar a HTB

OpenVPN y su integracion con NetworkManager estan incluidos, junto con las
herramientas de WireGuard. Descarga el perfil de tu entorno autorizado de HTB y
usa el editor de conexiones de NetworkManager, o importa el archivo desde terminal:

```bash
nmcli connection import type openvpn file ~/Descargas/tu-perfil.ovpn
nmcli connection show
nmcli connection up "nombre-importado" --ask
```

El nombre aparece al importar. Para terminar: `nmcli connection down "nombre-importado"`.
No se incluyen perfiles VPN, claves ni laboratorios locales.

## Atajos

| Atajo | Accion |
|---|---|
| Super+Intro | Terminal |
| Super+Espacio | Lanzador DMS |
| Super+P | Pi |
| Super+E / Super+B | Archivos / Brave |
| Super+O | Vista general |
| Super+flechas | Cambiar ventana o columna |
| Super+Shift+flechas | Mover ventana o columna |
| Super+RePag/AvPag | Cambiar espacio |
| Super+1/2/3 | Espacios 1, 2 y 3 |
| Super+F / Super+Shift+F | Columna ancha / pantalla completa |
| Super+R | Cambiar ancho de columna |
| Super+V | Alternar ventana flotante |
| Super+Q | Cerrar ventana |
| Super+Shift+L | Bloquear |
| Super+, | Ajustes DMS |
| Super+Shift+? | Ayuda de atajos |
| ImprPant | Captura |

## Personalizar hablando

Abre «Configurar mi sistema con Pi». Ejemplo:
«Deja la barra arriba, reduce las animaciones y añade un atajo para Z Code».
Pi lee ~/Sistema/AGENTS.md y modifica los archivos correspondientes.
`desk check` valida y construye; `desk apply` pide confirmacion y sudo para aplicar.
El agente es tu usuario normal y estas instrucciones no constituyen un sandbox.

DMS conserva los ajustes hechos con su GUI. `desk capture-desktop` los guarda en
el repositorio para futuras instalaciones. No se sobrescriben en cada reconstruccion.

## Sin red

La terminal, el escritorio y los documentos guardados funcionan sin red.
Descarga previamente el material de estudio permitido por cada proveedor.
Los agentes de nube y los labs remotos necesitan conexion; la IA local queda aplazada.

## Recuperacion

- Si un cambio impide iniciar el escritorio, selecciona una generacion anterior
  de NixOS en el menu de arranque.
- Si puedes abrir una terminal: `sudo nixos-rebuild switch --rollback`.
- El rollback no recupera apuntes, sesiones, bases de datos ni contraseñas.
- Restic esta instalado, pero falta elegir destino y configurar tus copias.
- Hay zram y suspension; la hibernacion no esta configurada.

## Comprobaciones en el HP

Wi-Fi, Bluetooth, audio/microfono, brillo, touchpad, bloqueo manual, cierre de tapa
y desbloqueo tras suspension; conectar una pantalla; compartir pantalla; abrir Orca,
Z Code, Brave, Firefox y Burp; probar Pi con tu proveedor de nube.
No dar el equipo por terminado antes de estas pruebas y de configurar las copias.
