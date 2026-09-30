# Correcciones de ajustes DMS

La version fijada, DMS 1.4.6, oculta la barra de desplazamiento cuando no esta
activa. Tambien muestra las categorias de atajos directamente en ingles aunque
el resto de la interfaz use español.

El paquete personal incorpora:

- Barra vertical visible siempre que haya contenido que no quepa, con un control mas ancho.
- Traducciones de categorias, instrucciones y avisos del panel de atajos.
- Include final de `dms/binds.kdl` en Niri para activar los atajos editados desde DMS.
- Creacion inicial de ese archivo sin sustituir atajos existentes.

La correccion se aplica sobre una copia del paquete original en
`packages/dms-personal.nix`. El binario y las versiones se conservan; no se instala
otra sesion. Los cambios QML y las traducciones son pequenos y comprobados;
si cambia el codigo original, la construccion falla para exigir una revision.
Las traducciones se mantienen en `desktop/dms-es.json`.

No se ha traducido todo DMS: se corrigen los textos de este panel y la navegacion
revisada. Otras paginas pueden conservar textos sin traducir del proyecto original.

Antes de aplicar en el equipo, comprueba `git status` en `~/Sistema`. Las preferencias
actuales de DMS y tus atajos se conservan. Tras reconstruir, vuelve a abrir Ajustes,
comprueba ambos paneles desplazables y cambia un atajo para verificar el include.

Fuente de la version revisada:
https://github.com/AvengeMedia/DankMaterialShell/tree/v1.4.6
