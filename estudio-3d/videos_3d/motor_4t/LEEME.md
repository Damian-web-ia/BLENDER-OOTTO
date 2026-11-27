# El motor por dentro (4 tiempos) · primer vídeo con Maite

| Qué | Detalle |
|---|---|
| **Qué es** | Reel vertical de unos 39,5 s: un motor de gasolina de un cilindro en corte, con los cuatro tiempos (admisión, compresión, explosión, escape), el despiece suspendido que se vuelve a montar y una rampa de velocidad. |
| **Fecha** | 27-11-2026 (Damián: "la chica ahora va a sustituir a Alex ... Va a explicar y va a tener voz de chica"; pieza elegida por Damián: motor de 4 tiempos). |
| **Estándar** | Skill maestra `skills/ekoruedas-automotive-cgi-4k`: 4K 2160x3840, 60 fps, Cycles, estudio oscuro, piezas con medidas reales, foco de cine. |
| **Presentadora** | Maite (personaje de Tripo, `biblioteca/personajes/tripo/maite`), voz Renata de Ootto (acento de España). Clod no habla: gestos, cara y efectos. |
| **Datos** | Medidas de un cilindro típico: diámetro 82 mm, carrera 86 mm, biela de 140 mm. Un ciclo completo = 2 vueltas del cigüeñal. A 3.000 rpm, cada cilindro tiene 3.000 ÷ 60 ÷ 2 = 25 explosiones por segundo (cuenta, no dato inventado). |

## Archivos
- `../../biblioteca/motor_4t_real.py`: el motor (bloque, cárter, camisa, culata con conductos, porta-levas, junta, refrigerante y aceite en corte; pistón con segmentos y bulón, biela, cigüeñal con contrapesos, polea y volante con corona; válvulas, muelles y levas; bujía de `bujia_real.py`; gas de la cámara) y su cinemática real (`poner_angulo`).
- `motor_4t.py`: la escena (estudio, peana con filo de luz, Maite, Clod, tiempos sincronizados con la voz, gas por colores, chispa, bola de fuego, mezcla que entra y humo que sale, apertura, despiece, rampa, 13 planos con cortes secos, anclas para el montaje).
- `voces_motor.json`: voz de Maite línea a línea con tiempos de palabra.
- `montaje_motor.json`: gancho, rótulos de piezas, títulos de los 4 tiempos, contador de explosiones, avisos de síntomas, logo final.
- `mezcla_motor.py`: sonido (voz, música electrónica con ducking, efectos de cada tiempo, motor que acelera, susto de Clod; -14 LUFS).
- `prueba_frames.py`: fotogramas de prueba rápidos.

## Render
`scripts/cola_motor_4t.py` (en el PC): espera si hay otro render 4K, renderiza con `render_cycles_bg.py` (4K, 60 fps, 64 muestras, OIDN, foco automático) con reintentos y codifica a `motor_4t_4k60.mp4`.
