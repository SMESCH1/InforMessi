# InforMessi

![Python](https://img.shields.io/badge/Python-3.12-blue)
![LLM](https://img.shields.io/badge/LLM-Claude%20%7C%20Groq%20%7C%20Ollama-green)
![Evals](https://img.shields.io/badge/Evals-checks%20%2B%20LLM--as--judge-orange)
![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-blue)
![CI](https://img.shields.io/badge/CI-GitHub%20Actions-black)
![License](https://img.shields.io/badge/license-MIT-blue)

Pipeline editorial automatizado que genera y publica mensajes diarios sobre la Selección Argentina y el Mundial 2026 en Telegram. Arquitectura híbrida: un agente Claude genera con web search, un gate de evals (checks programáticos + LLM-as-judge) valida, y Groq actúa como fallback de generación y como modelo juez.

🇬🇧 [English version below](#english-version)

---

## Qué hace

1. **Recolecta datos** — scraper diario de noticias (04:00 AR), eventos históricos, NewsAPI, Reddit, clima determinístico vía Open-Meteo.
2. **Genera la editorial** — un agente Claude Code programado (`.claude/routines/daily-editorial.md`, 09:15 AR) redacta el mensaje con web search verificado en 2+ fuentes y lo commitea como `source: claude-agent`. Si no corrió o su report no valida, el pipeline regenera con Groq 70B (`source: groq-fallback`); como último piso hay reports pre-generados (`source: pregenerated-base`).
3. **Valida con evals** — gate de calidad (`evals/run_evals.py`, 10:15 AR): 10 checks programáticos derivados de la guía editorial + LLM-as-judge (Groq, rúbrica 1-5, temp 0). Un `fail` marca `eval_warning` y bloquea toda publicación automática.
4. **Publica en Telegram** — preview con aprobación manual, edición, o publicación automática de respaldo a las 2 horas (nunca si hay `eval_warning`).
5. **Se ejecuta solo** — GitHub Actions + routine cloud corren todo diariamente.

> Dos piezas centrales: el **gate de evals** (generación separada de evaluación — genera Claude, juzga Llama; ver [docs/ai-engineering.md](docs/ai-engineering.md)) y el **sistema RAG anti-repetición** (memoria persistente de qué ya se dijo: `rag_memory_database.py`, `rag_memory_system.py`, `rag_style_learning.py`).

📚 Documentación clave: [docs/ai-engineering.md](docs/ai-engineering.md) (teoría y patrones de AI Engineering aplicados) · [docs/agente-diario.md](docs/agente-diario.md) (contrato agente ↔ pipeline) · [docs/architecture.md](docs/architecture.md) (arquitectura completa).

## Stack

- **Python 3.12** — lenguaje principal
- **Claude Code (scheduled agent)** — generación principal con web search (routine cloud 09:15 AR)
- **Groq API** — fallback de generación (llama-3.3-70b-versatile) y modelo del LLM-as-judge
- **Ollama** — LLM local opcional para desarrollo (qwen2.5:7b-instruct)
- **Evals propias** — `evals/checks.py` (10 checks) + `evals/judge.py` (judge con rúbrica)
- **Telegram Bot API** — preview privado + publicación en canal + webhook de aprobaciones
- **Flask + Render** — servidor del webhook
- **GitHub Actions** — scraper 04:00 AR y pipeline diario 10:15 AR
- **NewsAPI + Reddit (PRAW) + Open-Meteo** — fuentes de datos

## Arquitectura

```
04:00 AR  daily-news-scraper.yml ──► data/daily-news (noticias filtradas)

09:15 AR  Agente Claude (routine cloud)
          web search (2+ fuentes) + clima + memoria RAG
          evals propias (hasta 3 intentos)
                │ commit reports/HOY.json (source: claude-agent)
                ▼
10:15 AR  GitHub Actions (daily-informessi.yml)
                │
                ▼
          update-today-report.py
                ├─ report del agente fresco y válido ──► se usa tal cual
                └─ si no ──► generate-message.py + RAG (Groq 70B, source: groq-fallback)
                │
                ▼
          evals/run_evals.py --gate --judge --on-fail regenerate
                ├─ pass / pass_with_warnings ──► sigue
                └─ fail ──► eval_warning=true (bloquea auto-publish, exige humano)
                │
                ▼
          send-daily-report-review.py ──► chat privado (preview, con header ⚠ si eval_warning)
                │              ┌─────────────┐
                ├──────────────┤  Apruebo    │ ──► canal público
                │              ├─────────────┤
                ├──────────────┤  Edito      │ ──► edit-and-validate-report.py
                │              ├─────────────┤
                └──────────────┤  Sin acción │ ──► auto-publish-fallback.py (2h; nunca con eval_warning)
                               └─────────────┘
```

Detalle del flujo y los patrones aplicados: [docs/architecture.md](docs/architecture.md) y [docs/ai-engineering.md](docs/ai-engineering.md).

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
├── .claude/routines/          # daily-editorial.md (agente Claude programado)
├── .github/workflows/         # CI: daily-informessi.yml, daily-news-scraper.yml
├── assets/media/YYYY-MM-DD/   # imágenes scrapeadas por fecha
├── data/                      # events.json, memory-database.json, eval-history.json (runtime)
├── docs/                      # documentación interna (ai-engineering.md, agente-diario.md, ...)
├── evals/                     # checks.py, judge.py, run_evals.py (gate de calidad)
├── prompts/                   # prompts editoriales + judge-prompt.md
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

*(Summary — the Spanish version above is the canonical documentation.)*

InforMessi is a hybrid automated editorial pipeline that generates and publishes daily messages about the Argentine national team and the 2026 World Cup on Telegram.

**Key features:**
- **Generator/evaluator separation**: a scheduled Claude Code agent writes the daily editorial with web search (09:15 AR); a GitHub Actions pipeline (10:15 AR) validates it through an evals gate — 10 programmatic checks plus an LLM-as-judge (Groq llama-3.3-70b-versatile, temp 0, JSON mode, 1-5 rubric). Different models generate and judge.
- **Layered fallbacks**: Groq 70B regeneration if the agent's report is missing or invalid, plus pre-generated base reports as a last resort — all three sources go through the same evals gate.
- **Anti-hallucination grounding**: deterministic weather injection (Open-Meteo), post-generation entity whitelisting, 2-source web verification, and a custom **anti-repetition RAG system** (persistent memory of published content).
- **Human-in-the-loop with a circuit breaker**: Telegram review flow with manual approval, 2-hour auto-publish fallback, and an `eval_warning` flag that blocks all automatic publishing when evals fail.
- Deep dive (Spanish): [docs/ai-engineering.md](docs/ai-engineering.md).

**Stack:** Python 3.12 · Claude Code agent · Groq · Ollama · Telegram Bot API · Flask · Render · GitHub Actions · NewsAPI · PRAW (Reddit) · Open-Meteo

**Run locally:**
```bash
git clone https://github.com/SMESCH1/InforMessi.git && cd InforMessi
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# Set up .env (see config section above) then:
python3 scripts/generate-advance-reports.py --days 15
```

**Security:** `.env` is gitignored, CI validates no env files are tracked, secrets injected via GitHub Secrets. License: MIT.
