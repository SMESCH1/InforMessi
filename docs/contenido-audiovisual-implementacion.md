# Contenido Audiovisual - Implementación

Guía para usar el sistema de contenido audiovisual implementado.

## 🎯 Descripción

Sistema simple de detección automática de contenido audiovisual (imágenes/videos) para incluir en los informes diarios.

---

## 📁 Estructura de Directorios

```
assets/
└── media/
    ├── 2025-12-28/
    │   ├── imagen.jpg
    │   ├── video.mp4 (opcional)
    │   └── metadata.json (opcional)
    ├── 2025-12-29/
    │   └── imagen.png
    └── .gitkeep
```

**Formato de fecha:** `YYYY-MM-DD` (mismo formato que los informes)

---

## 🚀 Uso

### Paso 1: Crear Directorio para el Día

```bash
# Para hoy
mkdir -p assets/media/$(date +%Y-%m-%d)

# Para una fecha específica
mkdir -p assets/media/2025-12-28
```

### Paso 2: Agregar Contenido

```bash
# Copiar imagen
cp mi-imagen.jpg assets/media/2025-12-28/

# O mover
mv foto-del-dia.png assets/media/2025-12-28/
```

**Formatos soportados:**
- Imágenes: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
- Videos: `.mp4`, `.mov`, `.gif` (animados)

### Paso 3: (Opcional) Agregar Metadata

Crea `assets/media/2025-12-28/metadata.json`:

```json
{
  "description": "Messi en entrenamiento previo al Mundial",
  "source": "AFA",
  "photographer": "Fotógrafo AFA",
  "tags": ["entrenamiento", "messi", "seleccion"]
}
```

### Paso 4: El Sistema lo Detecta Automáticamente

Al generar o actualizar un informe:

```bash
python3 scripts/update-today-report.py --date 2025-12-28
```

El sistema:
- ✅ Detecta automáticamente si hay contenido para esa fecha
- ✅ Incluye contexto en el prompt del LLM
- ✅ Envía la imagen junto con el mensaje a Telegram

---

## 🔍 Verificar Contenido

```bash
# Verificar si hay contenido para una fecha
python3 scripts/detect-media.py --date 2025-12-28

# Verificar para hoy
python3 scripts/detect-media.py
```

---

## 📤 Envío a Telegram

Cuando envías un informe con contenido visual:

```bash
python3 scripts/send-daily-report.py --date 2025-12-28
```

**Automáticamente:**
- ✅ Detecta si hay imagen para esa fecha
- ✅ Envía la imagen con el mensaje como caption
- ✅ Si no hay imagen, envía solo el texto

---

## 🎨 Cómo Funciona

### 1. Detección

El script `detect-media.py` busca en `assets/media/YYYY-MM-DD/`:
- Archivos de imagen (`.jpg`, `.png`, etc.)
- Archivos de video (`.mp4`, `.mov`, etc.)
- Metadata opcional

### 2. Integración en Generación

Cuando se genera un mensaje:
- El sistema detecta si hay contenido visual
- Agrega contexto al prompt: "Hay X imagen(es) disponible(s)"
- El LLM puede mencionar el contenido visual si es relevante

### 3. Envío a Telegram

Cuando se envía el informe:
- Si hay imagen, se envía como foto con caption
- Si no hay imagen, se envía solo texto
- Si falla el envío de imagen, hace fallback a texto

---

## 📋 Ejemplo Completo

```bash
# 1. Crear directorio
mkdir -p assets/media/2025-12-28

# 2. Agregar imagen
cp ~/Downloads/messi-entrenamiento.jpg assets/media/2025-12-28/

# 3. (Opcional) Agregar metadata
cat > assets/media/2025-12-28/metadata.json << EOF
{
  "description": "Messi en entrenamiento",
  "source": "AFA"
}
EOF

# 4. Verificar
python3 scripts/detect-media.py --date 2025-12-28

# 5. Actualizar informe (detecta automáticamente)
python3 scripts/update-today-report.py --date 2025-12-28

# 6. Enviar (incluye imagen automáticamente)
python3 scripts/send-daily-report.py --date 2025-12-28
```

---

## ⚠️ Límites de Telegram

- **Fotos:** Máx. 10MB
- **Videos:** Máx. 50MB (recomendado < 20MB)
- **GIFs:** Máx. 10MB

Si el archivo es muy grande, Telegram rechazará el envío y se enviará solo el texto.

---

## 💡 Tips

1. **Nombres descriptivos:**
   - `messi-entrenamiento.jpg` es mejor que `IMG_1234.jpg`
   - Facilita identificar contenido después

2. **Una imagen principal:**
   - Si hay múltiples imágenes, se usa la primera
   - Considera organizar: `imagen-principal.jpg`, `imagen-2.jpg`

3. **Videos cortos:**
   - Para Telegram, videos cortos (< 20MB) funcionan mejor
   - Considera comprimir videos largos

4. **Metadata útil:**
   - Agrega metadata si quieres que el LLM tenga más contexto
   - Puede ayudar a generar mejores descripciones

---

## 🔄 Flujo Automático

Si usas GitHub Actions o cron:

1. **Agregas contenido manualmente** a `assets/media/YYYY-MM-DD/`
2. **El sistema lo detecta automáticamente** al generar/actualizar
3. **Se incluye en el informe** y se envía a Telegram

No requiere configuración adicional.

---

## 🧪 Testing

```bash
# 1. Crear directorio de prueba
mkdir -p assets/media/2025-12-28

# 2. Agregar imagen de prueba (o crear una dummy)
echo "test" > assets/media/2025-12-28/test.jpg

# 3. Verificar detección
python3 scripts/detect-media.py --date 2025-12-28

# 4. Probar en generación
python3 scripts/collect-daily-data.py --date 2025-12-28 --output test.json
python3 scripts/generate-message.py --data test.json --output test.txt
# Verificar que el prompt incluya mención de contenido visual
```

---

*Última actualización: 2025-12-28*

