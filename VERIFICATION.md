# Verificación

## 0.2.2-beta.1 — corrección de partida nueva / alpha47

- Generador SHA-256: `b00da2777600ace06f0f200d84e21798cd4e7452495a82b4934408d86e639e22` (103053824 bytes).
- Motor SHA-256: `d911b5f6597adb15eea65a35c6a67298a698efcacc4027c5927e1e7dfb0be531`.
- 170 pruebas del motor superadas, 3 ignoradas; ejecutable compilado.
- Generación completa nueva desde las dos ISO compatibles: salida0,324.4s,
  1170 referencias GLTF válidas, EXE de escritorio creado y comprobado.
  Hash, tamaño y fecha de las ISO originales se conservaron.
- Interfaz del generador renderizada y revisada en los cinco idiomas, en un
  escritorio aislado. El setup español escribió language_slot4 y fullscreen.
- Cinco rechazos de seguridad comprobados en este EXE: ruta relativa, misma ISO,
  ISO inválida, destino ocupado (archivo testigo intacto) y payload alterado.
- El fallo antiguo se reprodujo en alpha46: al sustituir el nivel tras la intro,
  una pasada Bgra8UnormSrgb recibía un pipeline de efectos Rgba8Unorm y el renderer
  terminaba. El proceso devolvía0 incluso con ese error; por eso no se usa exit0
  como único criterio de éxito.
- Alpha47, cooperativo: selección real mediante entradas internas programadas,
  tres vídeos de intro omitidos después de35 frames cada uno, cambio00→00 y
  vuelta a la jugabilidad con dos targets distintos640×720/MSAA4. Captura11000
  exacta1280×720, salida0, sin error de validación, revisada visualmente.
  No se afirma que se reprodujera la escena4 en ese recorrido cooperativo.
- Alpha47 recién generado: partida nueva con Ratchet desde sus propios datos
  extraídos, mismos vídeos omitidos, cambio00→00, escena4 completa842frames,
  y jugabilidad después. Captura11000 exacta1280×720, salida0, revisada visualmente.
- Jak individual también terminó la escena4 y volvió a jugar. En ese intento
  frío la compilación de shaders retrasó la captura19628 frente a10000: salida3.
  Se conserva como evidencia visual tardía, no como un pase de captura exacta.
- Se conservan otros dos intentos adversos del script cooperativo: el primero
  volvió al menú sin iniciar partida; el segundo tenía un rango inválido y salió101
  antes de las pruebas gráficas. No cuentan como pruebas de jugabilidad superadas.
- Auditoría por lista permitida y hashes:2384 archivos del payload; sin formatos
  comerciales, credenciales ni código decompilado en el árbol público. Lint del
  árbol público contra los datos de Ratchet y la instalación de Jak:0 fallos/0avisos.
  La licencia ISC redistribuible se conserva; no es un recurso comercial del juego.

Las pruebas nuevas son programadas y acotadas. Las confirmaciones físicas de
DualSense Bluetooth y reconexión pertenecen a builds anteriores; no se anuncia
una prueba física nueva ni compatibilidad universal. No se han completado las
campañas. Progreso global13/100. Las capturas4K históricas se identifican por versión;
las dos pruebas de transición exactas de esta release son720p.

El manifest sigue indicando `generated_not_gameplay_verified`: el generador no
certifica la jugabilidad de la instalación de cada usuario. La verificación nativa
se realizó aparte en una instalación de prueba. Las ISO y los registros privados
no se publican.


## Histórico: desarrollo interno alpha42

Motor interno SHA-256:
`37e393ff51de3ddb44e4bb9731fb9ceb7e75f9d7b084906717a76bc6fba12f23`.

840 pruebas del núcleo superadas / 1 ignorada; 169 del motor / 3 ignoradas;
ejecutable compilado. Cuatro clientes gráficos alpha42 completados con capturas
4K exactas y salida correcta: tramo de Kalebo cooperativo (frame 9200),
Swingshot (6220), agua/planeo (6680) y retorno magnético (9600). Son pruebas
programadas acotadas, sin comprobación física nueva ni campaña completada.
La prueba de agua/planeo no se presenta como un ensayo independiente de buceo
sostenido. El pulido visual de manos, compañeros y escapes sigue pendiente.

La selección publicada en `assets/seleccion-personajes-alpha42.png` es una
captura nueva del cliente con ese hash, frame 4600 exacto, salida 0 y dimensiones
3840×2160, revisada visualmente. Se utilizó un perfil separado, datos generados
previamente desde las ISO y entradas internas programadas. La ventana permaneció
oculta desde el arranque y sin audio; no se capturaron otras aplicaciones.
J2 sin dispositivo asignado es el estado real del ensayo.

En esa publicación histórica, la beta descargable conservaba alpha27 y los hashes siguientes.
La descarga actual es0.2.2/alpha47, descrita arriba. Véase [DEVELOPMENT.md](DEVELOPMENT.md)
para los resultados positivos, fallos conservados y trabajo pendiente.

## 0.2.1-beta.1 — START contextual / alpha27

La pantalla START muestra **una sola línea**. La familia de botones efectiva,
el dispositivo activo y la asignación física de Start determinan la indicación.
El teclado conserva ENTER como acceso de inicio. Al cambiar el dispositivo,
la indicación sigue el mismo enrutamiento usado por el menú.

- 169 pruebas del motor superadas; 2 ignoradas. La prueba nueva cubre familias,
  retorno a teclado y reasignación física del botón de inicio.
- Nueva generación completa desde las dos ISO: exit 0, 282.3 s,
  1170 referencias GLTF válidas y nuevo EXE del escritorio.
- START nativo de la instalación recién generada: frame 3200 exacto, exit 0,
  captura oculta de 3840×2160 revisada; únicamente PULSA ENTER.
- El cambio de texto según mando se verifica con pruebas sintéticas del código;
  no se atribuye una nueva pulsación física de DualSense a esta actualización.
- El motor conserva el código de campaña de alpha26; las pruebas de núcleo,
  cooperativo, menús francés/español y agua/planeo anteriores figuran abajo como
  referencia y no se presentan como nuevas ejecuciones de alpha27.
- Motor: `8ca7e846bbeb0edaaddba651396b331fe031d6f329c7673b99b7778ee32ee52d`
- Generador: `e8307a052d3b3cf0975b74d745d13125222cd8bb1448eb9f094524412ab94cf5`

### Captura de selección de personajes

Cliente nativo alpha27 / 0.2.1, hash 8CA7E846. Se abrió START, se eligió
Multijugador y se capturó el frame 4600 exacto, exit 0, con salida 3840×2160.
Imagen real revisada de dos paneles de selección y previews 3D. La ejecución
se mantuvo oculta desde el arranque, sin tomar el foco ni enviar teclas al sistema.
El segundo dispositivo sin asignar es el estado real de este ensayo. No se
afirma una nueva comprobación de dos mandos físicos ni se cambia el porcentaje
global por añadir la imagen.

## Referencia histórica: 0.2.0-beta.1 / alpha26

Fecha: **25 de octubre de 2026**. Motor **V19 alpha26 experimental**, basado en
la jugabilidad verificada de alpha24, con traducciones del menú y resolución del
monitor. No incluye el trabajo de agarres todavía sin verificar.

| Elemento | Resultado |
|---|---|
| Generador completo, dos ISO propias → instalación nueva | Superado, exit 0; 276.2 s |
| Ratchet compatible | USA SCUS_971.99 v1.00; ELF y extracción verificados |
| Jak compatible | USA SCUS_971.24; extracción y validación OpenGOAL superadas |
| Modelos y animaciones convertidos | 1170 referencias GLTF válidas; ojos restaurados; rigs y clips comprobados |
| ISO originales | Hash, tamaño y fecha preservados |
| Escritorio | EXE con icono creado; comprobación de lanzamiento superada |
| Cinco idiomas del setup | Render de interfaz, preflight y escritura de preferencias iniciales superados |
| Menú nativo | Francés y español, idioma leído de settings, sin RC_LANG forzado |
| Resolución física | Arranque fullscreen sin bordes observado a 3840×2160, frame 3840×2160 |
| Capturas posteriores | Ventanas ocultas desde el arranque, salida 3840×2160, sin tomar el foco |
| Cooperativo | Dos vistas verticales 1920×2160, MSAA 4; prueba programada de agua→impulso/planeo |
| SDL3 local | Inicialización 3.4.18 HIDAPI/XInput registrada por el cliente generado |
| Pruebas del núcleo | 821 superadas |
| Pruebas del motor | 168 superadas, 2 ignoradas |
| Rechazos de seguridad | 5 superados: ruta relativa, ISO duplicada, ISO inválida, destino ocupado, payload alterado |
| Auditoría del paquete | Sin ISO, modelos/texturas/audio comerciales, fuentes descompiladas ni credenciales |

La resolución fullscreen se observó en un arranque separado. Las capturas
publicadas proceden de ventanas ocultas y del render del juego; no capturan
otras aplicaciones ni el escritorio.

Las capturas de menú terminan en el frame 6400; la de agua/planeo en 6680.
La pantalla START con el logo nuevo sobre Veldin se capturó en el frame 4800.
Los cuatro clientes citados terminaron con exit 0 y se revisaron visualmente.
El idioma español inicial corresponde a la elección del setup de la instalación
probada; el perfil francés separado demuestra que el motor aplica ese idioma.

Las pruebas nativas usan entradas programadas y escenarios acotados, con mejoras
desbloqueadas para el ensayo. No prueban una progresión legítima hasta créditos.
Las 427 pruebas de integración históricas no se presentan como una ejecución
nueva de alpha26. Las pruebas que requieren recursos específicos pueden omitir
su cuerpo si no están disponibles; los clientes nativos aportan evidencia aparte.

La confirmación humana de DualSense Edge Bluetooth, navegación y reconexión es
de una build anterior. No hubo una nueva prueba física de dos mandos, USB,
Nintendo, Xbox ni compatibilidad universal en esta release.

## Integridad

- Motor: `f5d483623992f0d63760bc6e0f1334668f01a03eb706021f17fc4046ec125e1e`
- Generador: `a95ba2673edb7fad549e634f09bb8fecfc8f5bd87daf4227111245ef95e7dfeb`
- La release incluye `SHA256SUMS.txt` para comprobar la descarga.
- El payload embebido se verifica antes de ejecutar herramientas y cada archivo
  se vuelve a verificar tras extraerlo. La DLL de SDL3 está incluida localmente.

`build-manifest.local.json` conserva **generated_not_gameplay_verified**: una
generación correcta no demuestra que todas las campañas sean jugables. Los logs,
ISO, conversiones y rutas privadas de las pruebas no se publican.
