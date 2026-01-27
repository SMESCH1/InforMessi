# InforMessi - Sistema Automatizado de Informes Diarios

Sistema automatizado que genera y publica informes diarios sobre el Mundial de Fútbol 2026 y la Selección Argentina de Fútbol.

## 🎯 Descripción

InforMessi es un pipeline editorial automatizado que:
- Genera informes diarios con antelación (15 días)
- Actualiza automáticamente con noticias y eventos recientes
- Publica en Telegram con validación manual opcional
- Utiliza LLM local (Ollama) para generar contenido editorial

**Características principales:**
- ✅ Generación anticipada de informes
- ✅ Actualización diaria automática (GitHub Actions)
- ✅ Validación manual opcional (Telegram)
- ✅ Pre-aprobación de informes
- ✅ Publicación automática de respaldo
- ✅ Sistema de memoria RAG para evitar repeticiones
- ✅ Integración con múltiples fuentes (NewsAPI, Reddit, eventos)

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    FUENTES DE DATOS                         │
├─────────────────────────────────────────────────────────────┤
│  • NewsAPI (noticias)                                       │
│  • Reddit (r/soccer, r/argentina, r/fulbo, etc.)          │
│  • data/events.json (eventos manuales)                     │
│  • assets/media/ (contenido audiovisual)                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              RECOLECCIÓN DE DATOS                           │
│         (collect-daily-data.py)                            │
├─────────────────────────────────────────────────────────────┤
│  • Calcula días restantes al Mundial                       │
│  • Recolecta eventos del día                                │
│  • Recolecta noticias relevantes                            │
│  • Detecta contenido audiovisual                            │
│  • Determina sección semanal                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           GENERACIÓN DE MENSAJE (LLM)                      │
│         (generate-message.py)                              │
├─────────────────────────────────────────────────────────────┤
│  • Construye prompt con:                                    │
│    - Identidad editorial (system-prompt.md)                │
│    - Estructura del mensaje (main-editorial.md)            │
│    - Datos del día (eventos, noticias, sección semanal)   │
│    - Contexto de memoria RAG (evita repeticiones)          │
│  • Llama a Ollama (LLM local)                              │
│  • Genera mensaje de 90-130 palabras                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              ALMACENAMIENTO                                 │
│         (reports/YYYY-MM-DD.json)                          │
├─────────────────────────────────────────────────────────────┤
│  • Informe completo con datos y mensaje                    │
│  • Estados: draft → updated → published                     │
│  • Pre-aprobación opcional                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         ACTUALIZACIÓN DIARIA (GitHub Actions)              │
│    (10:15 AM Argentina - 13:15 UTC)                         │
├─────────────────────────────────────────────────────────────┤
│  1. Genera informe si no existe                             │
│  2. Actualiza con datos recientes                           │
│  3. Envía a preview (si no está pre-aprobado)              │
│  4. Publica automáticamente después de 2 horas              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         VALIDACIÓN MANUAL (Opcional)                        │
│         (Telegram - Chat Privado)                          │
├─────────────────────────────────────────────────────────────┤
│  • Botones: ✅ Aprobar | ❌ Rechazar | ✏️ Editar          │
│  • Webhook en Render procesa callbacks                      │
│  • Publica automáticamente en grupo público                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              PUBLICACIÓN                                    │
│         (Grupo Público de Telegram)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tecnologías Implementadas

### Backend
- **Python 3.12**: Lenguaje principal
- **Ollama**: LLM local para generación de contenido
  - Modelo configurable (por defecto: llama3.2)
  - Genera mensajes editoriales con identidad propia
- **Flask**: Servidor webhook para Telegram (Render)
- **GitHub Actions**: Automatización diaria

### APIs y Fuentes de Datos
- **NewsAPI**: Noticias sobre fútbol argentino y mundial
- **Reddit API (PRAW)**: Posts relevantes de subreddits
- **Telegram Bot API**: Envío y recepción de mensajes (grupos o canales)
- **Archivos JSON**: Eventos manuales y datos estructurados

### Almacenamiento
- **JSON Files**: Informes diarios en `reports/`
- **Base de Datos RAG**: `data/memory-database.json` (evita repeticiones)
- **Assets**: Contenido audiovisual en `assets/media/`

### Infraestructura
- **GitHub Actions**: Ejecución diaria automática
- **Render**: Hosting del servidor webhook (gratis)
- **Telegram**: Plataforma de publicación (grupos o canales)

---

## 🔄 Flujo Completo de Trabajo

### 1. Generación Anticipada (Manual - Opcional)

Genera informes para los próximos días:

```bash
python3 scripts/generate-advance-reports.py --days 15
```

**Qué hace:**
- Recolecta datos para cada día
- Genera mensaje con LLM
- Guarda en `reports/YYYY-MM-DD.json`
- Estado inicial: `draft`

### 2. Edición y Pre-Aprobación (Manual - Recomendado)

Edita y valida informes anticipadamente:

```bash
python3 scripts/edit-and-validate-report.py --date 2025-12-31
```

**Opciones:**
1. **Editar mensaje**: Modifica el contenido
2. **Validar sin editar**: Marca como pre-aprobado
3. **Cancelar**: No hace cambios

**Resultado:** Informe con `pre_approved: true` se publica directamente sin preview.

### 3. Actualización Diaria Automática (GitHub Actions)

**Cuándo:** Todos los días a las 10:15 AM (Argentina)

**Qué hace:**
1. Genera informe si no existe
2. Actualiza con noticias y eventos recientes
3. Regenera mensaje si hay cambios significativos
4. Envía a preview (si no está pre-aprobado)
5. Publica automáticamente después de 2 horas si no hay respuesta

### 4. Validación Manual (Opcional - Telegram)

Si el informe no está pre-aprobado:

1. **Recibes mensaje** en chat privado de Telegram
2. **Botones disponibles:**
   - ✅ **Aprobar**: Publica inmediatamente en grupo público
   - ❌ **Rechazar**: No publica
   - ✏️ **Editar**: Permite enviar versión editada
3. **Webhook procesa** automáticamente (Render)
4. **Se publica** en grupo público

### 5. Publicación Automática de Respaldo

Si no respondes en 2 horas:
- El sistema publica automáticamente
- Marca el informe como `auto_published: true`

---

## 📋 Proceso de Validación Manual

### Flujo con Webhook (Recomendado)

1. **GitHub Actions** envía informe a preview
2. **Recibes mensaje** en Telegram (chat privado)
3. **Haces clic** en botón (Aprobar/Rechazar/Editar)
4. **Webhook en Render** procesa el callback
5. **Se publica** automáticamente en grupo público

### Flujo sin Webhook (Alternativo)

Si el webhook no funciona, usa el script local:

```bash
python3 scripts/send-and-wait-local.py
```

Este script:
- Envía a preview
- Espera localmente tu respuesta
- Publica cuando apruebas

**Limitación:** Requiere que tu PC esté prendida.

---

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# Clonar repositorio
git clone <repo-url>
cd InforMessi

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar Ollama (si no lo tienes)
# Ver: docs/install-ollama.md
```

### 2. Configuración

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus API keys
nano .env
```

**Variables requeridas:**
```env
# Telegram
TELEGRAM_BOT_TOKEN=tu_token
TELEGRAM_PREVIEW_CHAT_ID=tu_chat_privado
TELEGRAM_PUBLIC_CHAT_ID=tu_grupo_publico

# APIs
NEWSAPI_KEY=tu_key
REDDIT_CLIENT_ID=tu_client_id
REDDIT_CLIENT_SECRET=tu_secret
REDDIT_USER_AGENT=tu_user_agent

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### 3. Configurar Webhook (Opcional pero Recomendado)

```bash
# Configurar webhook en Telegram
python3 scripts/setup-webhook.py --webhook-url https://tu-webhook.onrender.com
```

### 4. Generar Informes

```bash
# Generar informes para los próximos 15 días
python3 scripts/generate-advance-reports.py --days 15
```

Si querés generar informes anticipados **sin noticias** (para evitar repetir noticias viejas),
usá `--no-news` en la recolección de datos:

```bash
python3 scripts/collect-daily-data.py --date 2026-01-26 --output tmp/data-2026-01-26.json --no-news
```

---

## 📁 Estructura del Proyecto

```
InforMessi/
├── README.md                    # Este archivo
├── requirements.txt             # Dependencias Python
├── .env                         # Variables de entorno (no commitear)
├── .env.example                 # Ejemplo de variables
│
├── prompts/                     # Prompts para el LLM
│   ├── system-prompt.md        # Identidad editorial
│   ├── main-editorial.md       # Estructura del mensaje
│   └── examples.md             # Ejemplos de mensajes
│
├── data/                        # Datos estructurados
│   ├── events.json             # Eventos manuales
│   ├── players.json            # Jugadores para secciones
│   └── memory-database.json    # Base de datos RAG
│
├── scripts/                     # Scripts principales
│   ├── collect-daily-data.py   # Recolecta datos del día
│   ├── generate-message.py      # Genera mensaje con LLM
│   ├── generate-advance-reports.py  # Genera informes anticipados
│   ├── update-today-report.py  # Actualiza informe del día
│   ├── edit-and-validate-report.py  # Edita y pre-aprueba
│   ├── send-daily-report-review.py  # Envía a preview
│   ├── auto-publish-fallback.py     # Publicación automática
│   └── webhook-server.py       # Servidor webhook (Render)
│
├── reports/                     # Informes generados
│   └── YYYY-MM-DD.json         # Un informe por día
│
├── assets/                      # Contenido audiovisual
│   └── media/
│       └── YYYY-MM-DD/         # Media por fecha
│
├── .github/
│   └── workflows/
│       └── daily-informessi.yml # Workflow diario
│
└── docs/                        # Documentación
    ├── guia-agregar-contenido.md
    ├── guia-pre-aprobacion.md
    └── ...
```

---

## 📝 Estructura de un Informe

Cada informe en `reports/YYYY-MM-DD.json`:

```json
{
  "date": "2025-12-31",
  "generated_at": "2025-12-28T10:00:00",
  "status": "updated",
  "updated_at": "2025-12-31T08:00:00",
  "published_at": null,
  "pre_approved": false,
  "pre_approved_at": null,
  "data": {
    "date": "2025-12-31",
    "days_remaining": 163,
    "events": [...],
    "news": [...]
  },
  "message": "Buenos días 🇦🇷\n\n..."
}
```

**Estados:**
- `draft`: Generado anticipadamente
- `updated`: Actualizado con datos recientes
- `published`: Ya publicado en Telegram

**Pre-aprobación:**
- `pre_approved: true`: Se publica directamente sin preview
- `pre_approved: false`: Requiere validación manual

---

## 📚 Guías de Uso

### Agregar Contenido

- **[Guía: Agregar Contenido](docs/guia-agregar-contenido.md)**
  - Cómo agregar eventos
  - Cómo agregar contenido audiovisual
  - Cómo agregar noticias manuales
  - Formatos y ejemplos

### Pre-Aprobar Informes

- **[Guía: Pre-Aprobación](docs/guia-pre-aprobacion.md)**
  - Cómo editar informes
  - Cómo pre-aprobar
  - Flujo recomendado

### Configurar Canal de Telegram

- **[Guía: Configurar Canal](docs/guia-configurar-canal-telegram.md)**
  - Cómo usar un canal en lugar de un grupo
  - Obtener Chat ID del canal
  - Configuración paso a paso

### Configuración

- **[Guía: Configuración Inicial](docs/checklist-configuracion.md)**
- **[Guía: GitHub Actions](docs/github-actions-setup.md)**
- **[Guía: Render Webhook](docs/guia-render-setup.md)**

---

## 🔧 Scripts Principales

### Generación

```bash
# Generar informes anticipados
python3 scripts/generate-advance-reports.py --days 15

# Recolectar datos sin noticias (útil para anticipados)
python3 scripts/collect-daily-data.py --date 2026-01-26 --output tmp/data-2026-01-26.json --no-news

# Actualizar informe del día
python3 scripts/update-today-report.py
```

### Edición y Validación

```bash
# Editar y pre-aprobar informe
python3 scripts/edit-and-validate-report.py --date 2025-12-31
```

### Envío y Publicación

```bash
# Enviar a preview (o publicar si está pre-aprobado)
python3 scripts/send-daily-report-review.py

# Publicar informe aprobado manualmente
python3 scripts/publish-approved-report.py --date 2025-12-31
```

### Utilidades

```bash
# Verificar token del bot
python3 scripts/verify-bot-token.py

# Diagnosticar webhook
python3 scripts/diagnose-webhook-issue.py

# Probar flujos
python3 scripts/test-flujos-completos.py
```

---

## 🎯 Próximos Pasos

### Trabajo Diario (Sin Tocar Código)

1. **Agregar contenido:**
   - Eventos en `data/events.json`
   - Media en `assets/media/YYYY-MM-DD/`
   - Ver: `docs/guia-agregar-contenido.md`

2. **Pre-aprobar informes:**
   - Editar y validar con anticipación
   - Ver: `docs/guia-pre-aprobacion.md`

3. **Monitorear:**
   - Revisar logs de GitHub Actions
   - Verificar publicaciones en Telegram

### Mejoras Futuras (Opcional)

- [ ] Interfaz web para editar informes
- [ ] Sistema de versionado
- [ ] Más fuentes de datos
- [ ] Publicación en múltiples plataformas

---

## 🐛 Troubleshooting

### El workflow no se ejecuta

1. Verifica que el cron esté correcto: `15 13 * * *`
2. Verifica que el workflow esté habilitado
3. Ejecuta manualmente: Actions → Run workflow

### Los botones no funcionan

1. Verifica el webhook: `python3 scripts/setup-webhook.py --info`
2. Verifica que Render esté activo
3. Revisa logs de Render

### El LLM no genera mensajes

1. Verifica que Ollama esté corriendo: `ollama serve`
2. Verifica el modelo: `ollama list`
3. Verifica la URL en `.env`

---

## 📖 Documentación Adicional

- `docs/guia-agregar-contenido.md` - Cómo agregar eventos, media, noticias
- `docs/guia-pre-aprobacion.md` - Cómo pre-aprobar informes
- `docs/guia-pruebas-flujos.md` - Cómo probar todos los flujos
- `docs/sistema-memoria-rag.md` - Sistema de memoria para evitar repeticiones

---

## 🎨 Identidad Editorial

- **Tono**: Argentino, cercano, editorial
- **Estilo**: Informativo con humor sutil
- **Rigor**: No inventar datos, priorizar eventos reales
- **Cierre ritual**: "Coronados de gloria vivamos"

---

*Coronados de gloria vivamos* 🇦🇷
