# Estado del desarrollo — 26 de octubre de 2026

**Beta pública: 0.2.1-beta.1 / V19 alpha27. Progreso global: 13/100.**

La prioridad es terminar la campaña de Ratchet con Jak/Daxter. Los ensayos
siguientes pertenecen a builds internas posteriores y todavía no están incluidos
en el generador descargable.

## Selección de personajes

![Selección multijugador en la beta pública](assets/seleccion-personajes.png)

Captura real de alpha27, 3840×2160, frame 4600 exacto y salida correcta. Muestra
dos paneles con pareja, aspecto, dispositivo y vista 3D. El segundo dispositivo
figura sin asignar: las entradas de esta captura fueron programadas. Se conserva
la imagen ya publicada; no se presenta como una nueva prueba física.

## Avances comprobados y límites

| Área | Evidencia | Pendiente |
|---|---|---|
| Cornisas, alpha31 | Subida en individual y cooperativo, escenarios acotados con el cliente nativo y capturas 4K revisadas | Repertorio completo de niveles y recorridos de campaña |
| Botas magnéticas, alpha32 | Jak sobre paredes y techo originales de Orxon; tres clientes completados, capturas 4K revisadas | Regresiones y progresión normal hasta estas zonas |
| Cámara magnética cooperativa, alpha32 | Cámara propia siguiendo la gravedad de Jak; la otra vista permanece independiente; dos mitades de 1920×2160 con MSAA 4 | Más geometrías, transiciones y uso físico de dos mandos |
| Restauración de arma y cámara | Corrección implementada; 832 pruebas del núcleo superadas en esa revisión | Compilar y verificar en el cliente el retorno al suelo y el disparo posterior |
| Raíles y campaña completa | En desarrollo | Adaptación de raíles y campaña hasta créditos con Jak |

En la comparación de física de Orxon, 1060 posiciones del recorrido adaptado de
Jak coincidieron con las de Ratchet. Esto prueba ese recorrido y sus condiciones;
no equivale a terminar el nivel ni la campaña.

## Armas en superficies magnéticas

El comportamiento original guarda el arma durante el contacto magnético. Un
ensayo de alpha33 que esperaba disparos en el techo falló; se conserva como
resultado negativo. No se certifica disparo durante ese contacto.

La corrección posterior solicita recuperar el arma guardada y liberar las pistas
de cámara al volver a la locomoción normal de Jak. Su prueba de núcleo conserva
37 balas y recupera el arma esperada. Falta verificar la secuencia completa en
el cliente nativo: superficie magnética → suelo → cámara normal → apuntar y disparar.

Un diagnóstico posterior de 5000 ticks, con avance programado, no encontró un
retorno sano al suelo normal, tanto para Ratchet como para Jak. Se trata de una
búsqueda de ruta, sin actualización completa de objetos del mundo; no demuestra
un defecto exclusivo de Jak ni una salida del recorrido superada.

## Próximos hitos de esta adaptación

1. Verificar el retorno al suelo conservando arma, munición y cámara por jugador.
2. Repetir regresiones de agua, planeo, Swingshot y cornisas.
3. Comprobar guardado/carga en contexto magnético y adaptar raíles.
4. Recorrer la campaña de Ratchet con Jak hasta créditos antes de darla por completada.

Todas estas pruebas usan escenarios y entradas programadas. La confirmación
física histórica de DualSense Edge Bluetooth en menú y reconexión no se amplía
a estas builds. Ambas campañas completas, los viajes entre universos y la
compatibilidad completa con mandos siguen pendientes.

La descarga y sus hashes continúan documentados en [VERIFICATION.md](VERIFICATION.md).
