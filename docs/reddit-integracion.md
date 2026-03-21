# Integración con Reddit - Guía Completa

Guía para configurar y usar Reddit como fuente de información.

## 🎯 Descripción

El sistema scrapea subreddits relevantes para obtener posts sobre:
- Selección Argentina de Fútbol
- Mundial 2026
- Liga Profesional de Fútbol de Argentina
- Jugadores de la selección
- Noticias relacionadas

---

## 🔧 Configuración

### Opción 1: Con API de Reddit (PRAW) - Recomendado

**Ventajas:**
- ✅ Más confiable
- ✅ Respeta rate limits
- ✅ Mejor rendimiento

**Pasos:**

1. **Crear aplicación en Reddit:**
   - Ve a https://www.reddit.com/prefs/apps
   - Click en "create another app..." o "create app"
   - **Tipo:** "script" (importante: debe ser "script", no "web app")
   - **Nombre:** "InforMessi" (o el que prefieras)
   - **Descripción:** "Bot para scrapear posts sobre selección argentina" (opcional)
   - **Redirect URI:** `http://localhost:8080` ⚠️ **IMPORTANTE:** 
     - Puede ser cualquier URL válida (ej: `http://localhost`, `http://localhost:8080`, `https://example.com`)
     - **No se usa realmente** para aplicaciones tipo "script"
     - Solo es un campo requerido por Reddit, pero no se ejecuta
     - Usa `http://localhost:8080` como estándar
   - Click "create app"

2. **Obtener credenciales:**
   - **Client ID**: La cadena debajo del nombre de la app (ej: `abc123xyz`)
   - **Client Secret**: El "secret" que aparece (ej: `def456uvw`)
   - **User Agent**: `InforMessi/1.0` (o personalízalo)

3. **Agregar a `.env`:**
   ```env
   REDDIT_CLIENT_ID=tu_client_id
   REDDIT_CLIENT_SECRET=tu_client_secret
   REDDIT_USER_AGENT=InforMessi/1.0
   ```

4. **Instalar PRAW:**
   ```bash
   pip install praw
   ```

---

### Opción 2: Sin API (Scraping Directo)

**Ventajas:**
- ✅ No requiere configuración
- ✅ Funciona inmediatamente

**Desventajas:**
- ⚠️ Menos confiable (puede fallar si Reddit cambia estructura)
- ⚠️ Rate limits más estrictos

**Pasos:**

1. **Solo agregar User Agent a `.env`:**
   ```env
   REDDIT_USER_AGENT=InforMessi/1.0
   ```

2. **No instalar PRAW** (el script usará scraping directo)

---

## 📋 Subreddits Monitoreados

Por defecto, el sistema monitorea:

- `r/soccer` - Fútbol general
- `r/argentina` - Argentina general
- `r/fulbo` - Fútbol argentino
- `r/worldcup` - Mundial
- `r/messi` - Messi específico

**Puedes modificar** `SUBREDDITS` en `scripts/fetch-reddit.py` para agregar más.

---

## 🔍 Palabras Clave

El sistema filtra posts que contengan estas palabras clave:

- `argentina`, `seleccion argentina`, `scaloneta`
- `messi`, `di maria`, `martinez`, `de paul`, `mac allister`
- `mundial 2026`, `world cup 2026`, `qatar 2022`
- `liga profesional`, `superliga`, `primera division argentina`
- `afa`, `scaloni`, `campeon del mundo`

**Puedes modificar** `KEYWORDS` en `scripts/fetch-reddit.py` para agregar más.

---

## 🚀 Uso

### Manual

```bash
# Obtener posts de Reddit
python3 scripts/fetch-reddit.py --max-results 5

# Solo JSON (para integración)
python3 scripts/fetch-reddit.py --max-results 5 --json-only
```

### Automático

El sistema **automáticamente** obtiene posts de Reddit cuando ejecutas:

```bash
python3 scripts/collect-daily-data.py --date 2025-12-28 --output datos.json
```

Los posts de Reddit se combinan con las noticias y se incluyen en el informe.

---

## 📊 Formato de Datos

Los posts de Reddit se convierten al formato de noticias:

```json
{
  "title": "Título del post",
  "description": "Contenido del post (primeros 200 caracteres)",
  "url": "https://reddit.com/r/subreddit/comments/...",
  "source": "Reddit r/subreddit",
  "published_at": "2025-12-28T10:30:00"
}
```

---

## ⚙️ Configuración Avanzada

### Modificar Subreddits

Edita `scripts/fetch-reddit.py`:

```python
SUBREDDITS = [
    "soccer",
    "argentina",
    "fulbo",
    "worldcup",
    "messi",
    "tu_subreddit_aqui"  # Agregar más
]
```

### Modificar Palabras Clave

Edita `scripts/fetch-reddit.py`:

```python
KEYWORDS = [
    "argentina",
    "seleccion argentina",
    # ... agregar más keywords
]
```

### Ajustar Límite de Días

Por defecto, solo obtiene posts de los últimos 3 días. Para cambiar:

```python
# En fetch-reddit.py
cutoff_date = datetime.now() - timedelta(days=7)  # 7 días
```

---

## 🧪 Testing

```bash
# Probar obtención de posts
python3 scripts/fetch-reddit.py --max-results 3

# Verificar integración en recolección de datos
python3 scripts/collect-daily-data.py --date 2025-12-28 --output test.json
cat test.json | grep -i reddit
```

---

## ⚠️ Limitaciones

1. **Rate Limits:**
   - Sin API: ~60 requests/minuto
   - Con API: Depende de tu aplicación

2. **Filtrado:**
   - Solo posts de últimos 3 días
   - Solo posts relevantes (con keywords)

3. **Subreddits:**
   - Algunos subreddits pueden estar privados o no existir
   - El sistema continúa con otros si uno falla

---

## 💡 Consejos

1. **Usa API si planeas usar frecuentemente:**
   - Más confiable a largo plazo
   - Mejor rendimiento

2. **Ajusta keywords según necesidad:**
   - Agrega nombres de jugadores específicos
   - Agrega términos relevantes para tu audiencia

3. **Monitorea resultados:**
   - Revisa periódicamente qué posts se están capturando
   - Ajusta filtros si es necesario

---

*Última actualización: 2025-12-28*

