# BLENDER-OOTTO

Vídeos de **EKORUEDAS** (taller de neumáticos y mecánica en Derio, Bizkaia) protagonizados por **Alex** (el mecánico) y **Claude** (el robot aprendiz).

## Cómo se hace cada vídeo

1. **Guion**: texto de cada personaje, con humor e información útil sobre el coche.
2. **Voces (Ootto)**: Claude habla con la voz de Diego y Alex con la de Carlos. Ootto devuelve el momento exacto de cada palabra.
3. **Animación (Blender)**: Claude controla Blender por MCP. Los personajes se mueven al ritmo de esas palabras (boca, ojos, gestos, cámara).
4. **Render**: Blender renderiza el vídeo vertical 1080×1920 en el ordenador del taller.
5. **Montaje y publicación (Ootto)**: Ootto añade voz, subtítulos, música y efectos, y lo publica a las 19:00 en Instagram y YouTube. TikTok se sube a mano desde la app de Ootto.

## Carpetas

| Carpeta | Qué hay |
|---|---|
| `personajes/` | Personajes 3D reutilizables (`.blend`). |
| `escenarios/` | Decorados (taller, recepción, carretera...). |
| `scripts/` | Código Python de Blender que construye y anima cada vídeo. |
| `guiones/` | Texto de cada vídeo y tiempos de cada palabra de la voz. |
| `videos/sin-voz/` | Lo que sale de Blender, antes de añadir la voz. |
| `videos/final/AAAA-MM/` | El vídeo terminado tal y como se publica. |

Los archivos se nombran `AAAA-MM-DD_tema`.

## Personajes

- **Claude**: robot naranja pequeño con pantalla negra, ojos LED blancos, auriculares naranjas y el símbolo blanco en el pecho. Sin antena. Es entusiasta, torpe y gracioso.
- **Alex**: mecánico de unos 45 años con barba corta y mono negro liso con ribetes naranjas. Es serio y seco, y explica bien. Pendiente de modelar en 3D.

> El repositorio es público para que Ootto pueda importar los vídeos. No subir aquí nada privado.
