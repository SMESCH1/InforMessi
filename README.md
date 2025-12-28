# InforMessi - MVP v1

Sistema automatizado de generación diaria de mensajes informativos previos al Mundial de Fútbol 2026.

## 🎯 Descripción

InforMessi es un pipeline editorial automatizado que genera mensajes diarios sobre el Mundial 2026 y la Selección Argentina. El sistema genera informes con antelación (15 días) y los actualiza diariamente con las últimas noticias y eventos.

**Características principales:**
- ✅ Generación anticipada de informes (15 días)
- ✅ Actualización diaria automática con noticias y eventos actuales
- ✅ Almacenamiento accesible de informes en `reports/`
- ✅ Integración con Telegram para envío y revisión
- ✅ GitHub Actions para actualización automática

## 📋 Arquitectura MVP

```
┌─────────────────────┐
│  Generación         │
│  Anticipada         │
│  (15 días)          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  reports/           │
│  (almacenamiento)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Actualización      │
│  Diaria             │
│  (GitHub Actions)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Envío a Telegram   │
│  (Revisión humana)  │
└─────────────────────┘
```

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# Clonar repositorio
git clone <repo-url>
cd InforMessi

# Crear entorno virtual
bash setup-venv.sh

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys
```

### 2. Variables de Entorno

```env
# Telegram
TELEGRAM_BOT_TOKEN=tu_token
TELEGRAM_PREVIEW_CHAT_ID=tu_chat_id

# APIs
NEWSAPI_KEY=tu_key
OPENWEATHER_API_KEY=tu_key

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### 3. Generar Informes Anticipados

```bash
# Generar informes para los próximos 15 días
python3 scripts/generate-advance-reports.py --days 15
```

Los informes se guardan en `reports/YYYY-MM-DD.json`

### 4. Actualizar Informe del Día

```bash
# Actualizar informe de hoy con datos actuales
python3 scripts/update-today-report.py
```

### 5. Enviar Informe a Telegram

```bash
# Enviar informe del día a Telegram
python3 scripts/send-daily-report.py
```

## 📁 Estructura del Proyecto

```
InforMessi/
├── README.md                    # Este archivo
├── requirements.txt            # Dependencias Python
├── setup-venv.sh               # Script de setup
├── .env.example                 # Ejemplo de variables de entorno
├── prompts/                     # Prompts para el LLM
│   ├── system-prompt.md        # Identidad editorial
│   ├── main-editorial.md       # Prompt principal
│   └── examples.md             # Ejemplos
├── data/                        # Datos estructurados
│   ├── events.json             # Eventos del día
│   └── players.json            # Jugadores para secciones semanales
├── scripts/                     # Scripts principales
│   ├── collect-daily-data.py   # Recolecta datos del día
│   ├── generate-message.py     # Genera mensaje con LLM
│   ├── generate-advance-reports.py  # Genera informes anticipados
│   ├── update-today-report.py  # Actualiza informe del día
│   ├── send-daily-report.py    # Envía informe a Telegram
│   ├── fetch-news.py           # Obtiene noticias
│   ├── fetch-events-enhanced.py # Obtiene eventos
│   ├── validate-news.py        # Valida noticias
│   └── generate-weekly-sections.py # Genera secciones semanales
├── reports/                     # Informes generados
│   └── YYYY-MM-DD.json         # Un informe por día
├── .github/
│   └── workflows/
│       └── update-daily-report.yml  # GitHub Actions
└── docs/                        # Documentación
```

## 🔄 Flujo de Trabajo

### Generación Anticipada (Manual)

1. **Generar informes:**
   ```bash
   python3 scripts/generate-advance-reports.py --days 15
   ```
   - Genera informes para los próximos 15 días
   - Cada informe se guarda en `reports/YYYY-MM-DD.json`
   - Incluye datos del día y mensaje generado

### Actualización Diaria (Automática)

1. **GitHub Actions** ejecuta diariamente a las 8:00 AM UTC:
   - Actualiza el informe del día con noticias y eventos actuales
   - Hace commit y push de los cambios

2. **O manualmente desde PC local:**
   ```bash
   python3 scripts/update-today-report.py
   ```

### Envío a Telegram

```bash
python3 scripts/send-daily-report.py
```

- Carga el informe del día desde `reports/`
- Envía a Telegram para revisión
- Marca el informe como "published"

## 📝 Estructura de un Informe

Cada informe en `reports/YYYY-MM-DD.json` contiene:

```json
{
  "date": "2025-01-15",
  "generated_at": "2025-01-01T10:00:00",
  "status": "updated",
  "updated_at": "2025-01-15T08:00:00",
  "published_at": null,
  "data": {
    "date": "2025-01-15",
    "days_remaining": 512,
    "events": [...],
    "news": [...]
  },
  "message": "Buenos días 🇦🇷\n\n..."
}
```

**Estados:**
- `draft`: Informe generado anticipadamente
- `updated`: Informe actualizado con datos recientes
- `published`: Informe enviado a Telegram

## 🛠️ Scripts Principales

### `generate-advance-reports.py`

Genera informes con antelación.

```bash
python3 scripts/generate-advance-reports.py --days 15
```

### `update-today-report.py`

Actualiza el informe del día con datos actuales.

```bash
python3 scripts/update-today-report.py --date 2025-01-15
```

### `send-daily-report.py`

Envía el informe del día a Telegram.

```bash
python3 scripts/send-daily-report.py --date 2025-01-15
```

## 🔧 Configuración de GitHub Actions

1. **Agregar secrets en GitHub:**
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_PREVIEW_CHAT_ID`
   - `NEWSAPI_KEY`
   - `OPENWEATHER_API_KEY`

2. **El workflow se ejecuta automáticamente:**
   - Todos los días a las 8:00 AM UTC
   - Actualiza el informe del día
   - Hace commit y push

## 📚 Documentación

- `docs/flujo-completo.md` - Flujo completo del sistema
- `docs/editorial-guide.md` - Guía de estilo editorial
- `docs/architecture.md` - Arquitectura detallada

## 🎨 Identidad Editorial

- **Tono**: Argentino, cercano, editorial
- **Estilo**: Informativo con humor sutil
- **Rigor**: No inventar datos, priorizar eventos reales
- **Cierre ritual**: "Coronados de gloria vivamos"

## 📊 Próximos Pasos (Futuro)

- [ ] Interfaz web para editar informes
- [ ] Sistema de versionado de informes
- [ ] Integración con más fuentes de datos
- [ ] Publicación automática en múltiples plataformas

---

*Coronados de gloria vivamos* 🇦🇷
