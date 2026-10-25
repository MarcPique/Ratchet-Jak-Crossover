# Verificación

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
