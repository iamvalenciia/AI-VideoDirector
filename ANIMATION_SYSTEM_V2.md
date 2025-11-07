# Sistema de Animación V2 - Una Imagen por Segmento

## Problema Identificado

El sistema anterior generaba múltiples frames por segmento de audio, lo que causaba:
- Cambios de imagen durante el habla (antinatural y distractante)
- Descoordinación entre audio y frames
- Las imágenes no cubrían toda la duración del audio
- Transiciones bruscas que interrumpían la narrativa

## Solución Implementada

### 1. **Una Imagen por Segmento de Timestamps** ✅

**Concepto:** Cada segmento en `timestamps.json` representa una pausa natural en el habla (punto, coma, signo de exclamación/interrogación). Ahora generamos **EXACTAMENTE UNA IMAGEN** por cada segmento.

**Por qué funciona mejor:**
- Las imágenes cambian solo durante las pausas naturales del narrador
- El cambio visual coincide con el ritmo natural del habla
- Mayor claridad narrativa: imagen → narrador habla → pausa → nueva imagen
- Cobertura total del audio garantizada (cada segmento tiene su imagen)

**Ejemplo de sincronización:**
```
Segmento 1: "Wait until you hear about this." (0.00s - 2.45s)
  → frame_0001.png se muestra durante 2.45 segundos

Segmento 2: "The crypto world just changed forever," (2.45s - 5.12s)
  → frame_0002.png se muestra durante 2.67 segundos

... continúa para todos los segmentos hasta cubrir todo el audio
```

**Archivos modificados:**
- [`src/config/tasks.yaml`](src/config/tasks.yaml) - Task `create_animation_prompts`
  - Nueva descripción enfatizando "una imagen por segmento"
  - Eliminadas referencias a "progresión de frames"
  - Nuevo expected_output con estructura actualizada

### 2. **Transiciones de Crossfade (Desvanecimiento)** ✅

**Implementación:** Agregamos transiciones suaves de 300ms entre cada imagen.

**Cómo funciona:**
```python
crossfade_duration = 0.3  # 300ms

# Cada imagen (excepto la primera) hace fade-in
clip.crossfadein(crossfade_duration)

# Cada imagen (excepto la última) hace fade-out
clip.crossfadeout(crossfade_duration)
```

**Efecto visual:**
- Imagen actual se desvanece gradualmente (fade-out)
- Nueva imagen aparece gradualmente (fade-in)
- Transición elegante y profesional
- Sin cortes bruscos

**Archivos modificados:**
- [`src/tools/video_assembler_tool.py`](src/tools/video_assembler_tool.py):258-287

### 3. **Zoom Sutil Estilo Anime** ✅

**Cambios realizados:**

1. **Reducción del zoom:**
   - Antes: 5%-25% dependiendo de motion_intensity
   - Ahora: **8% constante** para todas las imágenes
   - Factor: `1.08` (zoom del 8%)

2. **Easing mejorado:**
   ```python
   # Ease-in-out para movimiento más natural
   eased_progress = progress * progress * (3.0 - 2.0 * progress)
   ```
   - Comienza lento
   - Acelera en el medio
   - Termina lento
   - Resultado: movimiento orgánico y elegante

3. **Dirección desde JSON:**
   - Cada frame especifica su zoom en el JSON: `"zoom_effect": "subtle_zoom_in"` o `"subtle_zoom_out"`
   - Alternancia inteligente para variedad visual
   - Control total desde la configuración

**Por qué 8% es perfecto:**
- Suficientemente sutil para no distraer
- Lo suficientemente notable para mantener interés
- Similar a técnicas de anime profesional
- Funciona con imágenes estáticas sin desenfocar

**Archivos modificados:**
- [`src/tools/video_assembler_tool.py`](src/tools/video_assembler_tool.py):30-82 (función `apply_ken_burns_zoom`)
- [`src/tools/video_assembler_tool.py`](src/tools/video_assembler_tool.py):138-192 (función `create_frame_clip`)

## Estructura JSON Actualizada

### animation_prompts.json (nuevo formato)

```json
{
  "base_image": "character_0001.png",
  "total_frames": 22,
  "video_duration": 60.30,
  "approach": "one_image_per_segment",
  "style_guidelines": "Black and white vector art, minimalist, high contrast",
  "frames": [
    {
      "frame_id": 1,
      "frame_filename": "frame_0001.png",
      "start_time": 0.00,
      "end_time": 2.45,
      "duration": 2.45,
      "segment_index": 0,
      "segment_text": "Wait until you hear about this.",
      "frame_type": "character_close_up",
      "shot_type": "medium_shot",
      "prompt": "Hooded figure with contemplative pose, index finger raised...",
      "composition": "centered",
      "emotional_tone": "mysterious_anticipation",
      "visual_metaphor": "secret_revelation",
      "transition_in": "crossfade",
      "zoom_effect": "subtle_zoom_in"
    },
    {
      "frame_id": 2,
      "frame_filename": "frame_0002.png",
      "start_time": 2.45,
      "end_time": 5.12,
      "duration": 2.67,
      "segment_index": 1,
      "segment_text": "The crypto world just changed forever,",
      "frame_type": "abstract_concept",
      "shot_type": "wide_shot",
      "prompt": "Abstract representation of transformation: circular mandala...",
      "composition": "radial",
      "emotional_tone": "dramatic_revelation",
      "visual_metaphor": "transformation",
      "transition_in": "crossfade",
      "zoom_effect": "subtle_zoom_out"
    }
  ]
}
```

### Campos clave nuevos:

- **`approach`**: `"one_image_per_segment"` - Identifica el nuevo enfoque
- **`segment_index`**: Índice del segmento en timestamps.json
- **`transition_in`**: `"crossfade"` - Tipo de transición
- **`zoom_effect`**: `"subtle_zoom_in"` o `"subtle_zoom_out"` - Dirección del zoom

### Validaciones:

✅ `total_frames` debe igualar el número de segmentos en `timestamps.json`
✅ `start_time` de cada frame coincide con el inicio del segmento
✅ `end_time` de cada frame coincide con el final del segmento
✅ No hay gaps entre frames
✅ El último frame termina exactamente en `video_duration`

## Flujo de Trabajo Actualizado

```
1. Script Creation (crew.py)
   ↓
2. Audio Generation (ElevenLabs)
   ↓
3. Whisper Transcription → timestamps.json
   ↓
4. Animation Director (NUEVO)
   - Lee timestamps.json
   - Cuenta segmentos (ej: 22 segmentos)
   - Genera 22 prompts (uno por segmento)
   - Output: animation_prompts.json
   ↓
5. Gemini Image Generation
   - Genera 22 imágenes (una por prompt)
   ↓
6. Video Assembly (MEJORADO)
   - Aplica zoom sutil (8%) a cada imagen
   - Aplica crossfade (300ms) entre transiciones
   - Sincroniza perfectamente con timestamps
   - Output: final_video.mp4
```

## Ventajas del Nuevo Sistema

### 🎯 Sincronización Perfecta
- Cada imagen dura exactamente lo que dura el segmento
- No hay descoordinación audio-visual
- Cobertura total del audio garantizada

### 🎨 Transiciones Elegantes
- Crossfade de 300ms entre imágenes
- Sin cortes bruscos
- Aspecto profesional y pulido

### 📱 Efecto Anime Sutil
- Zoom del 8% con easing suave
- Mantiene atención sin ser invasivo
- Dirección alternada (in/out) para variedad

### 💡 Narrativa Natural
- Cambios visuales en pausas naturales
- Respeta el ritmo del narrador
- Mayor claridad del mensaje

### 🔧 Eficiencia
- Menos imágenes a generar (~22 vs ~60-80)
- Menor costo de API (Gemini)
- Procesamiento más rápido

## Ejemplo de Timeline

```
Audio: 60 segundos
Segmentos: 22
Imágenes: 22

[====== Image 1 ======][====== Image 2 ======][====== Image 3 ======]
0s    "Wait..."    2.45s "Forever,"   5.12s  "Bitcoin..." 7.89s
      └─ pause ─┘          └─ pause ─┘           └─ pause ─┘
      Crossfade 300ms      Crossfade 300ms       Crossfade 300ms
      Zoom in 8%           Zoom out 8%           Zoom in 8%
```

## Próximos Pasos

Para usar el nuevo sistema:

1. **Ejecutar el crew completo** (genera script)
2. **Generar audio** con ElevenLabs
3. **Transcribir con Whisper** → `timestamps.json`
4. **Ejecutar Animation Director** → `animation_prompts.json` (ahora con 1 imagen por segmento)
5. **Generar imágenes** con Gemini (basado en los nuevos prompts)
6. **Ensamblar video** con las mejoras implementadas

## Archivos Modificados - Resumen

1. **`src/config/tasks.yaml`**
   - Task `create_animation_prompts` completamente reescrito
   - Nueva filosofía: una imagen por segmento
   - Expected output actualizado

2. **`src/tools/video_assembler_tool.py`**
   - `apply_ken_burns_zoom()`: Zoom reducido a 8%, easing mejorado
   - `create_frame_clip()`: Lee zoom_effect del JSON
   - `assemble_youtube_short()`: Implementa crossfade entre clips

## Resultados Esperados

✅ Sincronización perfecta entre audio y visuales
✅ Transiciones suaves y profesionales
✅ Efecto zoom sutil y elegante
✅ Menor costo de generación de imágenes
✅ Mayor claridad narrativa
✅ Aspecto más pulido y profesional

---

**Sistema V2 implementado el:** 2025-11-07
**Estado:** ✅ Listo para testing
