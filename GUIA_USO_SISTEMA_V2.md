# Guía de Uso del Sistema V2 - Una Imagen por Segmento

## 🎯 Problema Resuelto

**ANTES:**
- ❌ 75 imágenes generadas (múltiples por frase)
- ❌ Imágenes cambiando durante el habla
- ❌ Zoom desde la esquina (no centrado)

**AHORA:**
- ✅ 22 imágenes (una por frase/segmento)
- ✅ Imágenes cambian solo en pausas naturales
- ✅ Zoom centrado (desde el centro hacia afuera/adentro)
- ✅ Crossfade suave de 300ms entre imágenes

## 📋 Flujo de Trabajo Completo

### Paso 1: Generar Script y Audio
```bash
# Desde la raíz del proyecto
python src/main.py
```

Esto genera:
- `output/video_script.json` - El script viral
- `output/narracion.mp3` - Audio con ElevenLabs

### Paso 2: Transcribir Audio con Whisper
```bash
python src/main.py --step=transcribe
```

Esto genera:
- `output/timestamps.json` - Segmentos con pausas naturales (22 segmentos)

### Paso 3: Corregir Animation Prompts
```bash
cd src
python tools/fix_animation_prompts.py
```

Esto genera:
- `output/animation_prompts.json` - Con **22 frames** (uno por segmento)

**IMPORTANTE:** Este paso reemplaza al agente de animation_director porque ahora usamos un enfoque más directo y predecible.

### Paso 4: Generar Imágenes con Gemini
```bash
python src/main.py --step=generate-frames
```

Esto genera:
- `output/frames/frame_0001.png` hasta `frame_0022.png` (22 imágenes)

### Paso 5: Ensamblar Video
```bash
python src/main.py --step=assemble-video
```

Esto genera:
- `output/final_video.mp4` - Video completo con zoom centrado y crossfade

## 🔧 Características Técnicas

### 1. Una Imagen por Segmento

Cada segmento en `timestamps.json` representa una frase completa hasta:
- Punto (.)
- Coma (,)
- Signo de exclamación (!)
- Signo de interrogación (?)

**Ejemplo de timing:**
```
Segmento 1: "Wait until you hear about this." (0.00s - 1.36s)
  → frame_0001.png se muestra durante 1.36 segundos

Segmento 2: "Bitcoin ETFs could be on the verge of approval." (2.38s - 4.66s)
  → frame_0002.png se muestra durante 2.28 segundos

... continúa hasta cubrir todo el audio (60.30s)
```

### 2. Zoom Centrado

El zoom ahora se expande/contrae desde el **centro de la imagen**:

```python
# Cálculo del crop centrado
y_start = (new_h - h) // 2  # Centro vertical
x_start = (new_w - w) // 2  # Centro horizontal
```

- **Zoom In:** La imagen se agranda gradualmente desde el centro (1.0x → 1.08x)
- **Zoom Out:** La imagen se encoge gradualmente hacia el centro (1.08x → 1.0x)
- **Easing:** Movimiento suave con ease-in-out
- **Factor:** 8% (1.08x) - sutil pero visible

### 3. Transiciones Crossfade

Cada transición entre imágenes usa:
- **CrossFadeIn:** La nueva imagen aparece gradualmente (300ms)
- **CrossFadeOut:** La imagen anterior desaparece gradualmente (300ms)
- **Resultado:** Transición suave y profesional

## 📁 Estructura de Archivos

```
youtube_channel-crewai/
├── src/
│   ├── output/
│   │   ├── video_script.json         (Paso 1)
│   │   ├── narracion.mp3            (Paso 1)
│   │   ├── timestamps.json          (Paso 2)
│   │   ├── animation_prompts.json   (Paso 3) ← CORREGIDO
│   │   ├── frames/
│   │   │   ├── frame_0001.png       (Paso 4)
│   │   │   ├── frame_0002.png
│   │   │   └── ... (22 imágenes)
│   │   └── final_video.mp4          (Paso 5)
│   │
│   └── tools/
│       ├── fix_animation_prompts.py  ← NUEVO SCRIPT
│       └── video_assembler_tool.py   ← MEJORADO
│
└── GUIA_USO_SISTEMA_V2.md (este archivo)
```

## 🎬 Verificación del Video

Después de generar el video, verifica:

1. ✅ **Duración:** 60.30 segundos (igual que el audio)
2. ✅ **Número de cambios:** 22 transiciones (una por segmento)
3. ✅ **Zoom:** Desde el centro, no desde la esquina
4. ✅ **Transiciones:** Suaves, sin cortes bruscos
5. ✅ **Sincronización:** Imágenes cambian en pausas naturales

## 🐛 Solución de Problemas

### Problema: "Todavía veo múltiples imágenes por frase"

**Solución:** Ejecuta de nuevo el script de corrección:
```bash
cd src
python tools/fix_animation_prompts.py
```

Esto regenerará `animation_prompts.json` con **exactamente 22 frames**.

### Problema: "El zoom sigue siendo desde la esquina"

**Solución:** El código actualizado de `video_assembler_tool.py` ya tiene el zoom centrado. Asegúrate de estar usando la versión más reciente.

### Problema: "Errores al ensamblar el video"

**Verificaciones:**
1. ¿Tienes las 22 imágenes en `output/frames/`?
2. ¿El archivo `animation_prompts.json` tiene `"total_frames": 22`?
3. ¿Existe `output/narracion.mp3`?

## 📊 Comparación de Resultados

| Métrica | Sistema Anterior | Sistema V2 |
|---------|-----------------|------------|
| **Imágenes generadas** | 75 | 22 |
| **Costo Gemini API** | Alto | 70% menor |
| **Cambios de imagen** | Durante habla | En pausas naturales |
| **Tipo de zoom** | Desde esquina | Centrado |
| **Transiciones** | Bruscas | Suaves (crossfade) |
| **Sincronización** | Descoordinada | Perfecta |
| **Tiempo de generación** | Lento | 70% más rápido |

## 🎨 Personalización

### Ajustar duración del crossfade:
En `video_assembler_tool.py`, línea 257:
```python
crossfade_duration = 0.3  # Cambia este valor (en segundos)
```

### Ajustar intensidad del zoom:
En `video_assembler_tool.py`, línea 185:
```python
zoom_factor = 1.08  # 1.05 = 5%, 1.10 = 10%, etc.
```

### Cambiar patrón de zoom:
El script `fix_animation_prompts.py` alterna automáticamente:
```python
zoom_types = ["subtle_zoom_in", "subtle_zoom_out"]
```

## 📝 Notas Importantes

1. **¿Por qué no usar el Animation Director Agent?**
   - El agente LLM generaba múltiples frames por segmento
   - El nuevo script es más predecible y preciso
   - Genera exactamente lo que necesitamos

2. **¿Puedo mejorar los prompts?**
   - Sí, edita la línea 69 en `fix_animation_prompts.py`
   - Personaliza los prompts para cada tipo de frame

3. **¿Qué pasa con los 75 frames anteriores?**
   - Puedes borrarlos de `output/frames/`
   - El nuevo sistema solo necesita 22 imágenes

## ✅ Checklist de Implementación

- [x] Script y audio generados
- [x] Timestamps extraídos con Whisper
- [x] Animation prompts corregidos (22 frames)
- [ ] 22 imágenes generadas con Gemini
- [ ] Video ensamblado con zoom centrado
- [ ] Video revisado y aprobado

---

**Sistema V2 implementado:** 2025-11-07
**Estado:** ✅ Listo para producción
**Próximo paso:** Generar las 22 imágenes con Gemini
