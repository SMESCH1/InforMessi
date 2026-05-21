# InforMessi

![Python](https://img.shields.io/badge/Python-3.12-blue)
![LLM](https://img.shields.io/badge/LLM-Ollama%20%7C%20Groq-green)
![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-blue)
![CI](https://img.shields.io/badge/CI-GitHub%20Actions-black)
![License](https://img.shields.io/badge/license-MIT-blue)

Pipeline editorial automatizado que genera y publica mensajes diarios sobre la Selección Argentina y el Mundial 2026 en Telegram.

🇬🇧 [English version below](#english-version)

---

## Qué hace

1. **Recolecta datos** — eventos históricos, noticias (NewsAPI), Reddit, contenido audiovisual.
2. **Genera mensajes** — LLM local (Ollama) o API externa (Groq) con prompts editoriales y un sistema RAG anti-repetición.
3. **Publica en Telegram** — flujo de revisión con aprobación manual, edición o publicación automática de respaldo.
4. **Se ejecuta solo** — GitHub Actions corre el pipeline diariamente.

> Lo bueno acá es el **sistema RAG anti-repetición**: el bot mantiene memoria de qué ya dijo y cómo lo dijo, para no caer en clichés ni repetir información. Tres componentes: `rag_memory_database.py`, `rag_memory_system.py`, `rag_style_learning.py`.

## Stack

- **Python 3.12** — lenguaje principal
- **Ollama** — LLM local (qwen2.5:7b-instruct recomendado)
- **Groq API** — fallback gratuito en CI (sin Ollama)
- **Telegram Bot API** — publicación en canal/grupo + webhook para procesar aprobaciones
- **Flask + Render** — servidor del webhook
- **GitHub Actions** — ejecución diaria automatizada
- **NewsAPI + Reddit (PRAW)** — fuentes de noticias

## Arquitectura

```
GitHub Actions (cron diario 10:15 AR)
        │
        ▼
collect-daily-data.py ──► data/ (events, news, reddit)
        │
        ▼
generate-message.py + RAG ──► reports/YYYY-MM-DD.json
        │
        ▼
telegram-preview.py ──► chat privado (review)
        │              ┌─────────────┐
        ├──────────────┤  Apruebo    │ ──► publish-approved-report.py ──► canal público
        │              ├─────────────┤
        ├──────────────┤  Edito      │ ──► edit-and-validate-report.py
        │              ├─────────────┤
        └──────────────┤  Sin acción │ ──► auto-publish-fallback.py (al día siguiente)
                       └─────────────┘
```

## Inicio rápido (localhost)

```bash
git clone https://github.com/SMESCH1/InforMessi.git && cd InforMessi
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Crear .env con tus claves (ver "Configuración" abajo). NO subirlo al repo.

# Opcional: Ollama para LLM local
ollama pull qwen2.5:7b-instruct

# Generar informes para los próximos 15 días
python3 scripts/generate-advance-reports.py --days 15

# Probar envío a Telegram
python3 scripts/send-daily-report-review.py
```

## Configuración (`.env`)

Crear `.env` en la raíz (gitignored). En CI usar GitHub Secrets.

```env
# LLM
LLM_PROVIDER=ollama          # ollama o groq
LLM_MODEL=qwen2.5:7b-instruct
LLM_BASE_URL=http://localhost:11434
GROQ_API_KEY=                # solo si LLM_PROVIDER=groq

# Telegram
TELEGRAM_BOT_TOKEN=
TELEGRAM_PREVIEW_CHAT_ID=    # chat privado para revisión
TELEGRAM_PUBLIC_CHAT_ID=     # canal o grupo público

# Fuentes de datos
NEWSAPI_KEY=
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=InforMessi/1.0
```

## Estructura

```
.
├── .github/workflows/         # CI: daily-informessi.yml, daily-news-scraper.yml
├── assets/media/YYYY-MM-DD/   # imágenes scrapeadas por fecha
├── data/                      # events.json, players.json, world-cup-facts.json, memory-database.json
├── docs/                      # documentación interna
├── prompts/                   # prompts editoriales por contexto
├── reports/                   # YYYY-MM-DD.json (informes generados)
├── scripts/                   # 25+ scripts: collect, generate, edit, publish, webhook
└── tests/
```

## Seguridad

- ✅ `.env` excluido por `.gitignore`
- ✅ CI valida en cada run que no haya `.env*` versionado (step `Verificar que no haya archivos de entorno en el repo`)
- ✅ Claves vía `${{ secrets.* }}` en workflows

## License

MIT.

---

## English version

InforMessi is an automated editorial pipeline that generates and publishes daily messages about the Argentine national team and the 2026 World Cup on Telegram.

**Key features:**
- Data collection from NewsAPI, Reddit, and historical events
- Message generation with a local LLM (Ollama) or cloud API (Groq), powered by a custom **anti-repetition RAG system**
- Telegram review flow with manual approval, editing, or scheduled fallback publishing
- Daily execution via GitHub Actions cron

**Stack:** Python 3.12 · Ollama · Groq · Telegram Bot API · Flask · Render · GitHub Actions · NewsAPI · PRAW (Reddit)

**Run locally:**
```bash
git clone https://github.com/SMESCH1/InforMessi.git && cd InforMessi
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# Set up .env (see config section above) then:
python3 scripts/generate-advance-reports.py --days 15
```

**Security:** `.env` is gitignored, CI validates no env files are tracked, secrets injected via GitHub Secrets. License: MIT.
