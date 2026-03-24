# Guía de Configuración de APIs - InforMessi

Esta guía cubre la configuración de todas las APIs que utiliza el proyecto.

## Índice

1. [Groq API (LLM cloud)](#1-groq-api-llm-cloud)
2. [Telegram Bot API](#2-telegram-bot-api)
3. [NewsAPI (noticias)](#3-newsapi-noticias)
4. [Reddit API](#4-reddit-api)

---

## 1. Groq API (LLM cloud)

Groq es el proveedor de LLM cloud que se usa en GitHub Actions (donde Ollama local no está disponible).

### Obtener API Key

1. Crea una cuenta en [Groq Console](https://console.groq.com/)
2. Ve a **API Keys** y genera una nueva key
3. Copia la key (empieza con `gsk_...`)

### Configurar

En tu `.env`:

```env
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
GROQ_API_KEY=gsk_tu_key_aqui
```

Para uso local con Ollama, usa en su lugar:

```env
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5:7b-instruct
LLM_BASE_URL=http://localhost:11434
```

### Probar

```bash
python3 scripts/generate-advance-reports.py --days 1 --provider groq --with-news --overwrite
```

### Notas

- El tier gratuito de Groq tiene límites de requests por minuto
- En GitHub Actions, configura `GROQ_API_KEY` como repository secret
- El proyecto usa `qwen2.5:7b-instruct` para Ollama local y `llama-3.1-8b-instant` como modelo cloud recomendado

---

## 2. Telegram Bot API

Se necesitan un bot token y dos chat IDs (preview privado + canal público).

### Crear el Bot

1. Abre Telegram y busca **@BotFather**
2. Envía `/newbot` y sigue las instrucciones
3. Guarda el token (ej: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Obtener Chat IDs

1. Crea un grupo privado (para preview) y un canal público (para publicación)
2. Agrega el bot como administrador en ambos
3. Envía un mensaje en cada chat
4. Visita `https://api.telegram.org/bot<TOKEN>/getUpdates` para ver los chat IDs

O usa el script:

```bash
python3 scripts/get-telegram-chat-id.py
```

### Configurar

```env
TELEGRAM_BOT_TOKEN=tu_token
TELEGRAM_PREVIEW_CHAT_ID=-123456789
TELEGRAM_PUBLIC_CHAT_ID=-987654321
```

### Probar

```bash
python3 scripts/send-daily-report-review.py
```

Deberías recibir el mensaje en tu chat privado con botones de aprobación.

### Documentación adicional

- [Configuración de Telegram (dos chats)](configuracion-telegram-dos-chats.md)
- [Configuración del bot](telegram-setup.md)

---

## 3. NewsAPI (noticias)

NewsAPI provee noticias deportivas que se integran al mensaje diario. Es opcional: sin ella, el sistema usa RSS feeds y scraping como fallback.

### Obtener API Key

1. Crea una cuenta en [NewsAPI](https://newsapi.org/)
2. Obtén tu API key (gratis hasta 100 requests/día)

### Configurar

```env
NEWSAPI_KEY=tu_api_key
```

### Probar

```bash
python3 scripts/fetch-news.py
```

### Notas

- Si NewsAPI no está configurada, el sistema usa RSS feeds (TyC Sports, etc.)
- Si RSS también falla, intenta scraping como último recurso
- Las noticias se filtran por relevancia a la Selección Argentina y el Mundial

---

## 4. Reddit API

Reddit (via PRAW) provee contenido adicional de subreddits de fútbol argentino.

### Crear una aplicación Reddit

1. Ve a [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click en **Create App** (o **Create Another App**)
3. Selecciona **script**
4. Completa nombre y descripción
5. En **redirect uri** pon `http://localhost:8080`
6. Copia el **client ID** (debajo del nombre de la app) y el **secret**

### Configurar

```env
REDDIT_CLIENT_ID=tu_client_id
REDDIT_CLIENT_SECRET=tu_client_secret
REDDIT_USER_AGENT=InforMessi/1.0
```

### Probar

```bash
python3 scripts/fetch-reddit.py
```

### Documentación adicional

- [Integración con Reddit](reddit-integracion.md)

---

## Configuración completa del .env

Ver `.env.example` en la raíz del proyecto para una referencia completa de todas las variables.

---

## Probar todo junto

```bash
# 1. Recolectar datos del día
python3 scripts/collect-daily-data.py --output tmp/data.json

# 2. Generar mensaje
python3 scripts/generate-message.py --data tmp/data.json --output tmp/mensaje.txt

# 3. Enviar a Telegram para revisión
python3 scripts/send-daily-report-review.py
```

---

## Troubleshooting

### Groq no genera mensaje

- Verifica que `GROQ_API_KEY` esté en `.env` o en GitHub Secrets
- Verifica que el modelo exista en Groq (`llama-3.1-8b-instant` recomendado)
- Revisa límites de rate en la consola de Groq

### Noticias no se obtienen

- Verifica conexión a internet
- Si NewsAPI falla, el sistema usa RSS feeds automáticamente
- Prueba RSS directamente: `curl https://www.tycsports.com/rss/futbol.xml`

### Reddit no conecta

- Verifica que `REDDIT_CLIENT_ID` y `REDDIT_CLIENT_SECRET` sean correctos
- La app de Reddit debe ser de tipo **script**
- Reddit es opcional: sin él, el sistema funciona con NewsAPI y RSS

### Telegram no envía mensajes

- Verifica que el token sea correcto con `python3 scripts/verify-bot-token.py`
- Verifica que el bot esté agregado como admin en ambos chats
- Verifica que los chat IDs sean correctos (negativos para grupos/canales)
