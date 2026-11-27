# El turbo por dentro · Maite + Clod v3

| Qué | Detalle |
|---|---|
| **Qué es** | Reel vertical de unos 39,6 s: un turbocompresor real en corte seccional. Los gases de escape mueven la turbina (que se pone al rojo), el compresor aspira aire y lo mete apretado en el motor, despiece vertical suspendido que gira y se vuelve a montar, y el consejo del aceite y del ralentí. |
| **Fecha** | 27-11-2026, noche. Damián: "yo comenzaría ya a hacer en Blender el diseño 3D de cualquier material mecánico" y "aunque tome horas me da igual". |
| **Estándar** | Skill maestra `skills/ekoruedas-automotive-cgi-4k`: 4K 2160x3840, 60 fps, Cycles, estudio oscuro, piezas con medidas reales, corte seccional, despiece, macro y foco de cine. |
| **Personajes** | Maite explica (voz Renata de Ootto). Clod v3 no habla: intenta mover el turbo soplando ("Con soplar no basta, Clod"). |
| **Datos (con fuente)** | En los turbos pequeños el rotor llega a 300.000 rpm (folleto de averías de turbos de MAHLE Aftermarket). Turbina y compresor van unidos por un eje común y los mueven los gases de escape (RACE). Un turbo de gasolina ronda los 800-900 grados (Autofácil). Tras un trayecto exigente, dejar el motor al ralentí al menos un minuto antes de apagarlo, y respetar los cambios de aceite y filtro (Autofácil, "Dos claves para no romper el turbo"). |
| **Estado** | Lo produce y publica la sesión de Claude: el render 4K va en cola después del vídeo del motor. |

## Archivos
- `../../biblioteca/turbo_real.py`: el turbo (tamaño tipo GT17: rueda del compresor Ø38/49 mm con 6 + 6 álabes, rueda de la turbina Ø45/40 mm con 11 álabes, eje Ø8 mm, casquillos flotantes de bronce, cojinete axial, carcasa central con entrada y retorno de aceite, escudo térmico, caracolas de compresor y turbina, bridas con espárragos, wastegate con palanca, varilla y actuador). Se parte por y = 0 para el corte; el lado caliente se corta en su propia fundición, que brilla con `calor()`.
- `../../biblioteca/prueba_turbo.py`: fotos de prueba de la pieza sola (cerrada, corte, macro, al rojo, despiece).
- `turbo.py`: la escena (estudio del motor, columna de exposición, Maite, Clod v3, voz sincronizada, flujo de aire azul y gases naranjas, turbina al rojo con su luz, despiece vertical, 11 planos con cortes secos, anclas para el montaje).
- `voces_turbo.json`: voz de Maite (Renata) con tiempos de palabra y grupos de subtítulos.
- `montaje_turbo.json`: gancho, rótulos de piezas, avisos, contador de 0 a 300.000 rpm con su fuente, palabras clave en naranja y logo final.
- `mezcla_turbo.py`: sonido (voz, música con ducking, soplido de Clod, escape, silbido del turbo que sube y baja, aire, despiece, ralentí; -14 LUFS).
