# Código y empaquetado del generador

La descarga lista para usar está en Releases. El código de `src/` corresponde al
generador y a la conversión de recursos locales. El motor nativo de esta entrega
es un binario fijado por SHA-256; este repositorio no contiene el árbol privado
completo de desarrollo del motor ni recursos extraídos de los juegos.

El empaquetado de una release requiere una copia del motor verificado, shaders,
el extractor de ReRAC, el extractor/configuración de OpenGOAL, CPython con NumPy
y Pillow, y los DLL redistribuibles de Visual C++. `prepare_payload.py` usa una
lista permitida y rechaza formatos comerciales o modelos convertidos. Se
conservan las licencias en `licenses/` y dentro de la instalación generada.

`Build-Generator.ps1 -PayloadZip <payload.zip> -Branding <carpeta-logo>
-Output <generador.exe>` compila con el compilador de .NET Framework x64 de
Windows. La carpeta de branding debe contener `RatchetJak.ico` y
`RatchetJak-logo.png`. El ZIP se incorpora como recurso y se verifica por SHA-256
antes de ejecutar las herramientas. Cada archivo de su manifest se vuelve a
verificar después de extraer.

El generador final funciona sin Rust, Python externo ni descargas. Requiere las
dos ISO compatibles del usuario. Las únicas compilaciones locales durante la
generación producen el pequeño lanzador del escritorio con .NET; el motor del
juego ya está compilado.

`locales.json` contiene las traducciones propias del instalador y del menú
personalizado. Los idiomas de los datos originales se leen de las ISO. La
elección del setup inicializa `game/UserData/settings.toml`; después puede
cambiarse en Opciones. El lanzador selecciona fullscreen sin bordes, resolución
física de la ventana del monitor y escala interna 100 %.

No subas las carpetas generadas, las ISO ni registros que contengan rutas privadas.
