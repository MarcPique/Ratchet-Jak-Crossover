# Estado del desarrollo — 26 de octubre de 2026

**Beta pública: 0.2.1-beta.1 / V19 alpha27. Progreso global: 13/100.**

La prioridad es terminar la campaña de Ratchet con Jak/Daxter. Los ensayos
siguientes pertenecen a builds internas posteriores y todavía no están incluidos
en el generador descargable. No hay una nueva release en esta actualización.

## Selección de personajes

![Selección multijugador en la beta pública](assets/seleccion-personajes.png)

Captura real de alpha27, 3840×2160, frame 4600 exacto y salida correcta. Muestra
dos paneles con pareja, aspecto, dispositivo y vista 3D. El segundo dispositivo
figura sin asignar: las entradas de esta captura fueron programadas. Se conserva
la imagen ya publicada; no se presenta como una nueva prueba física.

## Avances comprobados y límites

| Área | Evidencia | Pendiente |
|---|---|---|
| Cornisas, alpha31 y regresión alpha35 | Subida en individual y cooperativo; cliente nativo y capturas 4K revisadas | Más niveles y recorridos legítimos de campaña |
| Botas magnéticas, alpha35 | Jak recorre pared y techo de Orxon y vuelve al suelo; pruebas individual y cooperativa de 9600 frames con capturas exactas y salida correcta | Progresión normal hasta estas zonas y más geometrías |
| Arma y cámara al salir, alpha35 | Recupera Blaster, apunta y dispara seis veces: 100→94 balas; la munición de J1 permanece en 100 | Otros gadgets, armas y transiciones |
| Regresiones, alpha35 | Agua→Hydro→impulso/planeo, Swingshot y cornisa comprobados en clientes nativos con capturas 4K revisadas | Repertorio completo de acciones y niveles |
| Guardado/carga de Jak como J2, alpha36 | Guarda mientras el arma está temporalmente recogida en la superficie magnética; otro proceso carga sin conceder objetos y dispara seis veces: 94→88 balas | Otros checkpoints y combinaciones de personajes |
| Confirmación de guardado, alpha36 | Corregido círculo=Sí en la confirmación original de sobrescritura; clic derecho cancela. Pausar desde J2 congela a ambos mientras J1 guarda | Comprobación física con dos mandos |
| Carga de Jak como personaje principal, alpha37 | La comparación reproduce un fallo: Ratchet recupera el arma al disparar; Jak permanece con la llave al pulsar R2 | Verificar la corrección en una nueva compilación y cliente nativo |
| Raíles y campaña completa | Pendientes | Adaptar raíles y recorrer la campaña hasta créditos con Jak |

En cooperativo, las pruebas aceptadas conservan dos imágenes distintas de
1920×2160 con MSAA 4 dentro de una captura de 3840×2160. Son comprobaciones
programadas de escenarios concretos, sin prueba física nueva de dos mandos.

## Armas y guardado en superficies magnéticas

Se respeta el comportamiento original: el arma se recoge durante el contacto
magnético. La prueba de alpha34 confirma que no se disparan balas en ese estado.
Un ensayo anterior que esperaba disparar en el techo falló y se conserva como
resultado negativo.

Alpha35 completa el recorrido de salida mediante movimiento programado relativo
a la cámara, sin teletransportar al personaje después de iniciar el escenario.
Tanto Jak individual como Jak en J2 vuelven a una plataforma normal de Orxon,
recuperan el arma y disparan. Esto no equivale a terminar el nivel ni la campaña.

En alpha36, el guardado de J2 conserva el arma prevista y sus 94 balas aunque
la mano viva esté ocupada por el contexto magnético. La carga positiva se realiza
en otro proceso, desde una copia privada de esa misma partida y con el mismo
EXE. Se confirma el aviso inicial de guardado y se verifican seis disparos reales,
sin añadir armas o munición al cargar. La plantilla y los archivos de partida
comprobados se mantienen sin cambios durante la carga.

El primer intento de carga de alpha36 se quedó esperando ese aviso inicial;
no se cuenta como aprobado. La comprobación positiva procede de otro cliente.

La comparación posterior de alpha37 revela un caso distinto en individual:
Ratchet recupera el Blaster y dispara tras cargar, pero Jak no lo recupera con
R2. Esto demuestra un problema de selección/disparo; no demuestra que la munición
se haya borrado. La adaptación de R2 supera 835 pruebas del núcleo, pero todavía
requiere compilar y probar el ejecutable nativo antes de declararla corregida.

## Próximos hitos

1. Verificar la recuperación del arma con R2 al cargar a Jak como personaje principal.
2. Comprobar que la adaptación mantiene las restricciones magnéticas y el disparo propio de J2.
3. Adaptar y probar raíles/cables frente al comportamiento original.
4. Recorrer la campaña de Ratchet con Jak hasta créditos antes de darla por completada.

Las poses, manos, anclajes de compañeros y escapes siguen siendo experimentales.
La confirmación física histórica de DualSense Edge Bluetooth en menú y reconexión
no se amplía a estas builds. Ambas campañas completas, los viajes entre universos
y la compatibilidad completa con mandos siguen pendientes.

La descarga y sus hashes continúan documentados en [VERIFICATION.md](VERIFICATION.md).
