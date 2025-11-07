# Video Assembly - YouTube Shorts Creator

## ¿Qué hace este paso?

El paso `assemble-video` toma los frames generados y el audio de narración para crear un video final en formato YouTube Shorts (1080x1920 píxeles).

## Características

✅ **Formato YouTube Shorts**: 1080x1920 píxeles (vertical)
✅ **Sincronización perfecta**: Los frames se sincronizan exactamente con el audio usando los timestamps de animation_prompts.json
✅ **Efectos visuales**: Zoom in/out dinámico basado en la intensidad de movimiento
✅ **Ajuste automático**: Las imágenes se redimensionan y centran automáticamente
✅ **Alta calidad**: Export a 30 FPS con codec H.264 y audio AAC

## Uso

### Comando básico

```bash
cd src
python main.py --step=assemble-video
```

### Requisitos previos

Asegúrate de tener:
1. `output/animation_prompts.json` - Metadata de frames
2. `output/narracion.mp3` - Audio de narración
3. `output/frames/frame_XXXX.png` - Todos los frames generados (frame_0001.png hasta frame_0023.png)

### Dependencias

El sistema instalará automáticamente:
- `moviepy>=1.0.3` - Para procesamiento de video
- `pillow>=10.4.0` - Para procesamiento de imágenes
- `numpy>=2.3.3` - Para operaciones matemáticas

Si tienes problemas de dependencias:

```bash
pip install moviepy pillow numpy
```

## Proceso de ensamblaje

El proceso tiene 5 pasos:

1. **Carga de metadata** - Lee animation_prompts.json
2. **Carga de audio** - Lee narracion.mp3
3. **Procesamiento de frames** - Ajusta y aplica efectos a cada frame
4. **Ensamblaje** - Compone el video final con audio
5. **Export** - Guarda el video como MP4

## Configuración avanzada

Si quieres personalizar el proceso, edita `src/tools/video_assembler_tool.py`:

```python
assemble_youtube_short(
    animation_prompts_path="output/animation_prompts.json",
    audio_path="output/narracion.mp3",
    frames_dir="output/frames",
    output_path="output/final_video.mp4",
    apply_effects=True,  # False para deshabilitar zoom
    fps=30  # Frames por segundo
)
```

## Efectos de Zoom

Los efectos de zoom se aplican automáticamente basándose en `motion_intensity` de animation_prompts.json:

- **low**: Zoom sutil de 5%
- **medium**: Zoom moderado de 15%
- **high**: Zoom dinámico de 25%

El tipo de zoom (in/out) se elige aleatoriamente para cada frame para crear variedad visual.

## Output

El video final se guarda en:
- **Ruta**: `output/final_video.mp4`
- **Formato**: MP4 (H.264 + AAC)
- **Resolución**: 1080x1920 (YouTube Shorts)
- **FPS**: 30
- **Bitrate**: 5000k
- **Duración**: Coincide con el audio

## Troubleshooting

### Error: MoviePy not installed
```bash
pip install moviepy
```

### Error: Frame not found
Verifica que todos los frames estén en `output/frames/` con el formato `frame_XXXX.png`

### Error: Audio file not found
Asegúrate de haber ejecutado:
```bash
python main.py --step=narrate
```

### Video muy largo para procesar
Esto es normal. El procesamiento puede tomar varios minutos dependiendo del número de frames y la duración del audio.

## Tiempo estimado

- **23 frames** (~42 segundos de audio): 2-3 minutos
- **50 frames** (~90 segundos de audio): 5-7 minutos
- **75 frames** (~120 segundos de audio): 8-12 minutos

## Próximos pasos

Una vez que el video esté listo:

1. Encuentra el archivo en `output/final_video.mp4`
2. Revisa el video con tu reproductor favorito
3. Sube a YouTube Shorts

### Recomendaciones para YouTube Shorts

- Máximo 60 segundos de duración
- Formato vertical (1080x1920) ✓
- Audio claro y sincronizado ✓
- Thumbnails llamativos (crea uno personalizado)
- Título atractivo con keywords
- Descripción con llamado a la acción

¡Tu YouTube Short está listo para viral! 🚀
