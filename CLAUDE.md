# InforMessi — Claude Code Guide

## Commands

```bash
# Run all tests (43 unit tests)
python3 -m pytest tests/ -v

# Run a single test file
python3 -m pytest tests/test_generate_message.py -v

# Generate advance reports (e.g. next 15 days)
python3 scripts/generate-advance-reports.py --days 15

# Refresh today's report with fresh news
python3 scripts/update-today-report.py

# Send today's report to Telegram for preview
python3 scripts/send-daily-report-review.py

# Inspect the anti-repetition memory database
python3 scripts/rag_memory_database.py --show

# Rebuild memory DB from scratch (only from published/pre_approved reports)
python3 scripts/rag_memory_database.py --update

# Launch editorial web UI (port 5001)
python3 scripts/webapp.py
# or: WEBAPP_PORT=8080 python3 scripts/webapp.py

# Publish a pre-approved report to Telegram
python3 scripts/publish-approved-report.py --date YYYY-MM-DD
```

## Architecture

### Report Lifecycle
Reports progress through these states:
`draft` → `updated` → `pre_approved` → `published`

The memory system (anti-repetition) is **only updated on publication**, not during drafting or
preview. Specifically, `analyze_report()` only registers news when `status` is `pre_approved`
or `published`. Drafts are never recorded.

### 2-Step RAG Pipeline
1. **Selection** — `generate-message.py` calls the LLM with `selection-prompt.md` to choose
   the most relevant events/news IDs from the available pool
2. **Generation** — the chosen items are injected into the full prompt (system + main-editorial +
   memory context + weekly section) and the LLM generates the final message

### Memory / Anti-repetition System (`rag_memory_database.py`)
- Persisted in `data/memory-database.json`
- Two-tier blocking in `build_memory_context_from_db()`:
  - **⛔ PROHIBIDO** — last 7 days (news) / 14 days (events/facts): never re-use
  - **⚠️ EVITAR** — 8–30 days (news) / 15–60 days (events/facts): use only as last resort
- `is_news_used_within(title, days=14)` and `is_event_used_within(desc, days=30)` replace the
  old all-history checks; old method names are backward-compatible wrappers
- Anniversary events (MM-DD matches today) get a 365-day window instead of 30 days
- `get_recent_topics(days=30)` now correctly filters by the `days` parameter

### News Freshness Scoring (`fetch-news.py`)
- `_add_freshness_score()` assigns: today=1.0, yesterday=0.8, 2 days ago=0.5, older=0.2
- News list is sorted by freshness before being returned
- Labels `[HOY]` / `[AYER]` / `[2 días]` / `[+3 días]` are injected into the selection prompt
  so the LLM can prioritize fresher news
- Default `--max-days` filter changed from 3 → 2

### LLM Providers
- **Ollama** — local development (`LLM_PROVIDER=ollama`, default model `qwen2.5:7b-instruct`)
- **Groq** — CI/CD (`.github/workflows/daily-informessi.yml`, `LLM_PROVIDER=groq`)

Provider is selected via env vars; both share the same prompt interface in `generate-message.py`.

### Event Matching
Historical events use **MM-DD** format (not YYYY-MM-DD) to support anniversary logic across
years. When querying or adding events, match on month-day only (e.g. `"03-08"`).

### Weekly Sections
Day-specific editorial sections are injected at generation time by `generate_weekly_sections.py`:
- Mon/Fri → Selección Argentina en Mundiales
- Tue/Thu → Jugador de la Scaloneta
- Sat → Dato Mundialista
- Sun → Dato del País Sede

### Editorial Web UI (`scripts/webapp.py`)
Flask app on port 5001 (override with `WEBAPP_PORT`). Does NOT conflict with
`webhook-server.py` which uses port 5000.
- `/` — dashboard: next 15 days, status badges, previews
- `/report/<date>` — edit view: textarea + word counter (target 90–130 words),
  event/news cards with freshness badges, memory panel showing blocked items
- `POST /api/report/<date>/save` — update message in JSON
- `POST /api/report/<date>/pre-approve` — toggle pre_approved ↔ draft
- `POST /api/report/<date>/regenerate` — re-run `generate-message.py` (timeout 90s)

## Critical Files

| File | Purpose |
|------|---------|
| `scripts/generate-message.py` | Core LLM generation logic (selection + generation steps) |
| `scripts/rag_memory_database.py` | Anti-repetition memory (RAG store, two-tier blocking) |
| `scripts/fetch-news.py` | News fetching with freshness scoring |
| `scripts/webapp.py` | Editorial web UI (Flask, port 5001) |
| `scripts/generate_weekly_sections.py` | Day-of-week editorial section injector |
| `scripts/rag_style_learning.py` | Style RAG from edited past reports |
| `scripts/collect-daily-data.py` | Assembles the daily data JSON (events + news) |
| `scripts/publish-approved-report.py` | Publishes pre_approved report to Telegram |
| `scripts/webhook-server.py` | Telegram webhook receiver (port 5000) |
| `data/events.json` | 300+ historical events keyed by MM-DD (96 KB) |
| `data/memory-database.json` | Persistent anti-repetition memory DB |
| `prompts/` | 5 LLM prompt files (system, main-editorial, selection, constraints, examples) |
| `.github/workflows/daily-informessi.yml` | Daily automation (CI/CD, uses Groq) |

## Key Conventions

- Reports are stored in `reports/YYYY-MM-DD.json` with keys: `date`, `status`, `message`, `data`
- `data` sub-object contains `events` (list) and `news` (list)
- Tests live in `tests/` — all 43 must pass before merging
- Memory is only updated when a report reaches `pre_approved` or `published` state
- Event data keys are MM-DD strings (e.g. `"03-08"`); never use full YYYY-MM-DD for event lookups
- Word count target for generated messages: **90–130 words**
- `selection-prompt.md` must never instruct the LLM to return empty lists when content exists;
  always select the least-recently-used item as fallback
