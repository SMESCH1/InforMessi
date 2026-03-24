# Contenido Audiovisual - Evaluación e Implementación

Evaluación de complejidad y propuesta de implementación para agregar contenido audiovisual al MVP.

## 📊 Evaluación de Complejidad

### Opción 1: Directorio Manual (Recomendada para MVP) ⭐

**Complejidad: Baja** 🟢

**Descripción:**
- Guardas archivos en `assets/media/` organizados por fecha
- El sistema detecta automáticamente si hay contenido para el día
- Se incluye en el informe y se envía a Telegram

**Ventajas:**
- ✅ Muy simple de implementar
- ✅ Control total sobre qué contenido incluir
- ✅ No requiere APIs externas
- ✅ Funciona offline
- ✅ Fácil de mantener

**Desventajas:**
- ⚠️ Requiere agregar contenido manualmente
- ⚠️ No hay generación automática

**Trabajo manual:**
- ~2-5 minutos por día para seleccionar/guardar contenido

---

### Opción 2: Generación Automática con APIs

**Complejidad: Alta** 🔴

**Descripción:**
- Integración con APIs de imágenes (Unsplash, Pexels)
- Generación de imágenes con IA (DALL-E, Midjourney)
- Búsqueda automática de contenido relevante

**Ventajas:**
- ✅ Completamente automático
- ✅ Sin trabajo manual

**Desventajas:**
- ❌ Requiere APIs adicionales (costos)
- ❌ Calidad puede variar
- ❌ Puede no coincidir con tu estilo
- ❌ Más complejo de implementar

---

## 🎯 Recomendación: Opción 1 (Directorio Manual)

Para el MVP, la opción más práctica es usar un directorio manual con detección automática.

### Estructura Propuesta

```
assets/
├── media/
│   ├── 2026-01-15/
│   │   ├── imagen.jpg
│   │   ├── video.mp4 (opcional)
│   │   └── metadata.json (opcional)
│   ├── 2026-01-16/
│   │   └── imagen.jpg
│   └── .gitkeep
└── README.md
```

### Funcionamiento

1. **Tú guardas contenido:**
   - Creas carpeta `assets/media/YYYY-MM-DD/`
   - Guardas imagen/video ahí
   - Opcional: `metadata.json` con descripción

2. **Sistema detecta automáticamente:**
   - Al generar informe, busca contenido para esa fecha
   - Si existe, lo incluye en el informe
   - Se envía junto con el mensaje a Telegram

3. **Si no hay contenido:**
   - El sistema funciona normalmente sin contenido visual

---

## 🚀 Implementación Propuesta

### Paso 1: Script de Detección

```python
# scripts/detect-media.py
def get_media_for_date(date: str) -> Dict:
    """Detecta contenido audiovisual para una fecha"""
    media_dir = PROJECT_ROOT / "assets" / "media" / date
    
    if not media_dir.exists():
        return None
    
    # Buscar archivos de imagen/video
    images = list(media_dir.glob("*.jpg")) + list(media_dir.glob("*.png"))
    videos = list(media_dir.glob("*.mp4")) + list(media_dir.glob("*.gif"))
    
    return {
        "has_media": len(images) > 0 or len(videos) > 0,
        "images": [str(img) for img in images],
        "videos": [str(vid) for vid in videos],
        "metadata": load_metadata(media_dir)
    }
```

### Paso 2: Integración en Generación

```python
# En generate-message.py
media = get_media_for_date(data["date"])
if media and media["has_media"]:
    prompt += f"\n### Contenido Visual Disponible\n"
    prompt += f"Hay {len(media['images'])} imagen(es) disponible(s) para este día.\n"
    prompt += "Menciona el contenido visual en el mensaje si es relevante."
```

### Paso 3: Envío a Telegram

```python
# En send-daily-report.py
if media and media["has_media"]:
    # Enviar imagen/video junto con mensaje
    send_telegram_photo(chat_id, media["images"][0], caption=message)
else:
    # Enviar solo texto
    send_telegram_message(chat_id, message)
```

---

## 📋 Estructura de Metadata (Opcional)

Si quieres agregar descripciones o contexto:

```json
// assets/media/2026-01-15/metadata.json
{
  "description": "Messi en entrenamiento previo al Mundial",
  "source": "AFA",
  "photographer": "Fotógrafo AFA",
  "tags": ["entrenamiento", "messi", "seleccion"]
}
```

---

## 🎨 Tipos de Contenido Soportados

### Imágenes
- `.jpg`, `.jpeg`
- `.png`
- `.gif` (animados)

### Videos
- `.mp4` (cortos, < 20MB para Telegram)
- `.gif` (animados)

### Límites de Telegram
- **Fotos**: Máx. 10MB
- **Videos**: Máx. 50MB (pero recomendado < 20MB)
- **GIFs**: Máx. 10MB

---

## 🔧 Configuración Mínima

### 1. Crear estructura

```bash
mkdir -p assets/media
touch assets/media/.gitkeep
```

### 2. Agregar contenido manualmente

```bash
# Para el 15 de enero de 2026
mkdir -p assets/media/2026-01-15
cp mi-imagen.jpg assets/media/2026-01-15/
```

### 3. El sistema lo detecta automáticamente

No requiere configuración adicional.

---

## 📊 Comparación de Opciones

| Característica | Manual | Automático |
|---------------|--------|------------|
| **Complejidad** | Baja | Alta |
| **Trabajo manual** | 2-5 min/día | 0 min/día |
| **Control** | Total | Limitado |
| **Costo** | $0 | Variable |
| **Calidad** | Tu elección | Variable |
| **Tiempo implementación** | 1-2 horas | 1-2 días |

---

## 💡 Recomendación Final

**Para MVP: Usar directorio manual**

1. **Implementación rápida**: 1-2 horas
2. **Control total**: Tú eliges qué contenido incluir
3. **Sin costos**: No requiere APIs
4. **Escalable**: Fácil agregar generación automática después

**Flujo de trabajo:**
- Cada día (o cuando tengas tiempo), guardas 1-2 imágenes relevantes
- El sistema las detecta y las incluye automáticamente
- Si no hay contenido, funciona normalmente sin imágenes

