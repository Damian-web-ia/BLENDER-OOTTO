# Despiece 3D del amortiguador (27-11-2026)

Reel vertical 1080x1920, 30 fps, 30,5 s. Hecho entero en Blender (EEVEE) en el PC de Damián, con Alex y Clod.
Plan A del canal: un despiece en 3D de una pieza del coche (después del neumático y de los frenos).

| Qué | Dónde / detalle |
|---|---|
| **Idea** | De Claude, por petición de Damián (27-11, 12:43): "vete haciendo vídeos de despieces ... cada vídeo tiene que ser mejor que el anterior". |
| **Voz** | Solo Alex, voz Diego (España), 4 frases. Clod no habla: bota, señala, se tapa la cara, cabecea y se balancea. |
| **Datos comprobados** | El muelle aguanta el peso; el amortiguador frena el rebote obligando al aceite a pasar por válvulas pequeñas y convierte el movimiento en calor (Diariomotor, Mapfre). Síntomas: flota, cabecea al frenar, se balancea en curvas, pierde aceite (RACE, Motor.es). Dato: con amortiguadores en mal estado la distancia de frenado aumenta hasta un 35 % (RACE). |
| **Modelo** | `estudio-3d/biblioteca/amortiguador_real.py`: McPherson con muelle, copela, fuelle, cuerpo, tubo de presión, aceite, pistón con 6 válvulas y láminas, válvula de pie, soporte con tornillos. Versión "gastado" con película de aceite y gotas. |
| **Escena** | `despiece_amortiguador.py` (abre antes `biblioteca/personajes/alex/alex_v2_rig.blend`). Usa el taller, el coche y los personajes del despiece del neumático. |
| **Montaje** | `montaje_amortiguador.py`: gancho que bota, subtítulos palabra a palabra, rótulos con línea a cada pieza, gráfico del rebote (sin / con amortiguador), síntomas uno a uno, nuevo frente a gastado, dato del RACE con contador y cierre "Síguenos". |
| **Sonido** | `mezcla_amortiguador.ogg` (-14,6 LUFS): voz, música electronic-minimal con ducking, efectos en cada evento (botes, explosión, muelle, aceite, válvulas, calor). |
| **Vídeo final** | `estudio-3d/videos/2026-11-27_despiece_amortiguador_voz_diego.mp4` (30,5 s, -15,4 LUFS, pico -0,9 dBTP) y portada `2026-11-27_despiece_amortiguador_portada.jpg`. Copias en el PC: `CLAUDE VIDEOS` y `evolucion_videos`. Render: 915 fotogramas al 67 %, 48 muestras, unos 2,5 s por fotograma (unos 40 min). |
| **Publicación** | Viernes 27-11-2026 a las 20:30 (Madrid), con la **v2** (materiales pro, 100 %, raytracing: `estudio-3d/videos/2026-11-27_despiece_amortiguador_v2_calidad_pro.mp4`). Instagram + YouTube por Ootto: reel 63551 (`media_d5edb3e3f8`, portada `media_d059e9fcf5`); la v1 (reel 63427) se canceló antes de salir. TikTok por vidIQ: post `846a4ae6-9919-47b4-92cd-56309e5f61aa` con la v2. |
| **v2 (27-11, tarde)** | Damián: "el aceite parecía solamente un color". Mismo vídeo con `biblioteca/materiales_pro.py` (aceite líquido con refracción, ondas y burbujas; cromo, acero mecanizado, pintura con barniz, goma, corte metálico) y `render_pro` (100 %, 64 muestras, raytracing). Render: 915 fotogramas, unos 6 s cada uno (1 h 35 min). Comparativa: `estudio-3d/videos/antes_y_ahora_amortiguador.jpg`. |
| **Novedades frente a los frenos** | Corte por la mitad en lugar de rayos X (se ve el interior limpio), gráfico animado, temblor de cámara en la explosión, plano corto de Alex con el dato, Alex fuera de plano mientras la pieza flota, cierre con pregunta. |

## Planos (fotogramas)
1-149 gancho (Clod bota en el capó; rayos X a la rueda; estalla en 120) · 150 muelle · 214 se quita el muelle y se abre por la mitad (gráfico) · 297 vástago, pistón y aceite · 357 válvulas · 453 calor · 533 consejo · 650 nuevo frente a gastado · 719 aviso final con el dato · 850 síguenos · fin 915.

## Lecciones
- Los rayos X en una pieza con varias capas (tubo + tubo interior + aceite) se ven como cristal esmerilado: para enseñar el interior, mejor un corte por la mitad con las caras de corte en naranja.
- Dentro del coche la pieza tiene que ir a escala (0,68) para no atravesar la carrocería; crece al salir.
- Un gráfico necesita al menos 2,5 s en pantalla: se alargó el plano del amortiguador hasta "el vástago".
