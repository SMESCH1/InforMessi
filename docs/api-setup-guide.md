# Guía de Configuración de APIs - InforMessi

Esta guía te ayudará a configurar todas las APIs necesarias para InforMessi.

## 📋 Índice

1. [Clima - OpenWeatherMap](#1-clima---openweathermap)
2. [Noticias - RSS Feeds y NewsAPI](#2-noticias---rss-feeds-y-newsapi)
3. [Eventos - JSON, Wikipedia y Calendario](#3-eventos---json-wikipedia-y-calendario)

---

## 1. Clima - OpenWeatherMap

### Opción A: OpenWeatherMap (Recomendado)

#### Paso 1: Obtener API Key

1. Ve a [OpenWeatherMap](https://openweathermap.org/api)
2. Crea una cuenta gratuita
3. Ve a "API keys" en tu perfil
4. Copia tu API key (gratis hasta 1000 llamadas/día)

#### Paso 2: Configurar

Agrega a tu archivo `.env`:

```env
WEATHER_API_KEY=tu_api_key_aqui
```

#### Paso 3: Probar

```bash
python3 scripts/fetch-weather.py
```

Deberías ver:
```
📍 AMBA:
   Min: 15°C
   Max: 22°C
   Descripción: Parcialmente nublado
```

### Opción B: Sin API (Datos por defecto)

Si no configuras la API, el sistema usará datos por defecto. Funciona pero no será real.

---

## 2. Noticias - RSS Feeds y NewsAPI

### Opción A: RSS Feeds (Gratis, Recomendado)

Los RSS feeds no requieren API key y son gratuitos.

#### Fuentes Disponibles

- **TyC Sports**: `https://www.tycsports.com/rss/futbol.xml`
- **Olé**: (si tienen RSS disponible)
- **Otros**: Agregar más feeds según necesidad

#### Configuración

No requiere configuración. El script `fetch-news.py` ya incluye feeds por defecto.

#### Probar

```bash
python3 scripts/fetch-news.py
```

### Opción B: NewsAPI (Opcional)

Si quieres más fuentes de noticias:

#### Paso 1: Obtener API Key

1. Ve a [NewsAPI](https://newsapi.org/)
2. Crea una cuenta gratuita
3. Obtén tu API key (gratis hasta 100 requests/día)

#### Paso 2: Configurar

Agrega a tu archivo `.env`:

```env
NEWSAPI_KEY=tu_api_key_aqui
```

#### Paso 3: Probar

```bash
python3 scripts/fetch-news.py
```

### Opción C: Scraping (Fallback)

Si RSS y NewsAPI fallan, el script intentará hacer scraping de TyC Sports.

**Nota**: El scraping puede romperse si la estructura del sitio cambia.

---

## 3. Eventos - JSON, Wikipedia y Calendario

### Opción A: Archivo JSON (Principal)

Los eventos principales deben estar en `data/events.json`.

#### Estructura

```json
{
  "events": [
    {
      "date": "2024-12-15",
      "type": "birthday",
      "priority": "high",
      "person": "Lionel Messi",
      "age": 37,
      "description": "Cumpleaños de Lionel Messi"
    },
    {
      "date": "2024-12-20",
      "type": "match",
      "priority": "critical",
      "description": "Argentina vs Brasil",
      "competition": "Amistoso"
    }
  ]
}
```

#### Agregar Eventos

Edita `data/events.json` y agrega tus eventos:

```bash
# Ver eventos actuales
cat data/events.json

# Editar (usa tu editor favorito)
nano data/events.json
```

### Opción B: Wikipedia (Eventos Históricos)

El script `fetch-events-enhanced.py` busca eventos históricos de fútbol en Wikipedia.

**No requiere configuración**, se ejecuta automáticamente.

### Opción C: Calendario (Cumpleaños)

El script incluye un calendario básico de cumpleaños. Puedes extenderlo editando `scripts/fetch-events-enhanced.py`.

---

## Instalación de Dependencias

Para que todo funcione, instala las dependencias:

```bash
pip install requests beautifulsoup4 feedparser
```

O si usas `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## Configuración Completa del .env

Ejemplo de `.env` completo:

```env
# Telegram
TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_PREVIEW_CHAT_ID=-123456789
TELEGRAM_PUBLISH_CHAT_ID=-987654321

# Clima
WEATHER_API_KEY=tu_openweathermap_key

# Noticias (opcional)
NEWSAPI_KEY=tu_newsapi_key

# LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

---

## Probar Todo Junto

Una vez configurado, prueba el flujo completo:

```bash
# 1. Recolectar datos
python3 scripts/collect-daily-data.py --output /tmp/datos-hoy.json

# 2. Verificar datos
cat /tmp/datos-hoy.json | python3 -m json.tool

# 3. Generar mensaje
python3 scripts/generate-message.py --data /tmp/datos-hoy.json --output /tmp/mensaje.txt

# 4. Ver mensaje
cat /tmp/mensaje.txt
```

---

## Troubleshooting

### Clima no funciona

- Verifica que `WEATHER_API_KEY` esté en `.env`
- Prueba la API directamente: `curl "http://api.openweathermap.org/data/2.5/weather?q=Buenos Aires,AR&appid=TU_KEY&units=metric"`
- Si falla, el sistema usará datos por defecto

### Noticias no se obtienen

- Verifica conexión a internet
- Prueba RSS feeds directamente: `curl https://www.tycsports.com/rss/futbol.xml`
- Si NewsAPI falla, el sistema usará RSS o scraping

### Eventos no aparecen

- Verifica que `data/events.json` exista y tenga formato correcto
- Verifica que la fecha coincida (formato YYYY-MM-DD)
- Los eventos de Wikipedia son opcionales y pueden no aparecer siempre

---

## Próximos Pasos

1. ✅ Configura clima (OpenWeatherMap)
2. ✅ Configura noticias (RSS o NewsAPI)
3. ✅ Agrega eventos a `data/events.json`
4. ✅ Prueba el flujo completo
5. ✅ Ajusta según necesidad

---

*Una vez configurado, el sistema funcionará automáticamente cada día*

