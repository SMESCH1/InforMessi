# 🚀 Configuración Rápida de APIs - InforMessi

Guía rápida para configurar clima, noticias y eventos.

## 📦 Paso 0: Configurar Entorno Virtual

**IMPORTANTE**: Este proyecto usa un entorno virtual (venv) para las dependencias.

### Activar el entorno virtual

```bash
# Activar venv (hacer esto cada vez que trabajes en el proyecto)
source venv/bin/activate

# Verás (venv) en tu prompt cuando esté activo
```

### Si no tienes venv creado

```bash
# Opción 1: Usar el script automático
bash setup-venv.sh

# Opción 2: Manual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Desactivar venv

```bash
deactivate
```

---

## 🌤 Paso 1: Configurar Clima (OpenWeatherMap)

### Obtener API Key

1. Ve a: https://openweathermap.org/api
2. Crea cuenta gratuita (toma 2 minutos)
3. Ve a "API keys" en tu perfil
4. Copia tu API key
5. **Gratis**: 1000 llamadas/día (más que suficiente)

### Configurar

Edita tu archivo `.env` y agrega:

```env
WEATHER_API_KEY=tu_api_key_de_openweathermap
```

**Ejemplo**:
```env
WEATHER_API_KEY=abc123def456ghi789jkl012mno345pq
```

### Probar

```bash
# Asegúrate de tener el venv activado
source venv/bin/activate

# Probar clima
python3 scripts/fetch-weather.py
```

**✅ Deberías ver**:
```
📍 AMBA:
   Min: 15°C
   Max: 22°C
   Descripción: Parcialmente nublado
```

**⚠️ Si no funciona**: El sistema usará datos por defecto (funciona igual, pero no será real).

---

## 📰 Paso 2: Configurar Noticias (Opcional)

### Opción A: RSS Feeds (Gratis, Ya Funciona)

**No requiere configuración**. El script ya incluye feeds de TyC Sports.

Solo prueba:

```bash
source venv/bin/activate
python3 scripts/fetch-news.py
```

### Opción B: NewsAPI (Opcional, Más Fuentes)

Si quieres más fuentes de noticias:

1. Ve a: https://newsapi.org/
2. Crea cuenta gratuita
3. Obtén tu API key
4. **Gratis**: 100 requests/día

Agrega a `.env`:

```env
NEWSAPI_KEY=tu_api_key_de_newsapi
```

### Probar

```bash
source venv/bin/activate
python3 scripts/fetch-news.py
```

**✅ Deberías ver** noticias relacionadas con fútbol argentino.

---

## 📅 Paso 3: Configurar Eventos

### Opción A: Archivo JSON (Principal)

Edita `data/events.json` y agrega tus eventos:

```json
{
  "events": [
    {
      "date": "2024-12-24",
      "type": "birthday",
      "priority": "high",
      "person": "Lionel Messi",
      "age": 37,
      "description": "Cumpleaños de Lionel Messi"
    },
    {
      "date": "2024-12-25",
      "type": "match",
      "priority": "critical",
      "description": "Argentina vs Brasil",
      "competition": "Amistoso"
    }
  ]
}
```

**Formato de fecha**: `YYYY-MM-DD` (ej: `2024-12-24`)

**Prioridades**: `critical`, `high`, `medium`, `low`

### Opción B: Automático (Wikipedia + Calendario)

**No requiere configuración**. El script busca eventos históricos automáticamente.

### Probar

```bash
source venv/bin/activate
python3 scripts/fetch-events-enhanced.py
```

**✅ Deberías ver** eventos del día desde JSON, calendario y Wikipedia.

---

## 🧪 Paso 4: Probar Todo Junto

```bash
# Activar venv
source venv/bin/activate

# Probar todas las APIs
bash scripts/test-apis.sh
```

O manualmente:

```bash
source venv/bin/activate

# Recolectar todos los datos
python3 scripts/collect-daily-data.py --output /tmp/datos-hoy.json

# Ver datos
cat /tmp/datos-hoy.json | python3 -m json.tool
```

---

## ✅ Checklist de Configuración

- [ ] Entorno virtual creado y activado (`source venv/bin/activate`)
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] `WEATHER_API_KEY` configurado en `.env` (opcional pero recomendado)
- [ ] `NEWSAPI_KEY` configurado en `.env` (opcional)
- [ ] Eventos agregados a `data/events.json` (recomendado)
- [ ] Prueba ejecutada: `bash scripts/test-apis.sh`

---

## 📝 Ejemplo de .env Completo

```env
# Telegram
TELEGRAM_BOT_TOKEN=tu_token
TELEGRAM_PREVIEW_CHAT_ID=-123456789
TELEGRAM_PUBLISH_CHAT_ID=-987654321

# Clima (recomendado)
WEATHER_API_KEY=tu_openweathermap_key

# Noticias (opcional)
NEWSAPI_KEY=tu_newsapi_key

# LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

---

## 🆘 Troubleshooting

### "Module not found" o "No module named 'feedparser'"

**Solución**: Asegúrate de tener el venv activado:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Clima no funciona

- Verifica que `WEATHER_API_KEY` esté en `.env`
- Prueba la API directamente:
  ```bash
  curl "http://api.openweathermap.org/data/2.5/weather?q=Buenos Aires,AR&appid=TU_KEY&units=metric"
  ```
- Si falla, el sistema usará datos por defecto (funciona igual)

### Noticias no se obtienen

- Verifica conexión a internet
- RSS feeds pueden fallar si el sitio está caído
- El sistema intentará múltiples fuentes automáticamente

### Eventos no aparecen

- Verifica formato de fecha en `events.json` (YYYY-MM-DD)
- Verifica que la fecha coincida con el día actual
- Los eventos de Wikipedia son opcionales

---

## 🎯 Próximos Pasos

Una vez configurado:

1. ✅ Activa el venv: `source venv/bin/activate`
2. ✅ Prueba el flujo completo: `bash scripts/test-full-flow.sh`
3. ✅ Genera un mensaje de prueba
4. ✅ Revisa en Telegram
5. ✅ Ajusta según necesidad

---

## 💡 Tips

- **Siempre activa el venv** antes de ejecutar scripts Python
- Puedes agregar `alias activate-informessi='cd /ruta/a/InforMessi && source venv/bin/activate'` a tu `.zshrc`
- El sistema funciona sin APIs configuradas (usa datos por defecto)
- Las APIs mejoran la calidad pero no son obligatorias

---

**💡 Tip**: Puedes empezar sin configurar nada. El sistema funcionará con datos por defecto y mejorará cuando agregues las APIs.
