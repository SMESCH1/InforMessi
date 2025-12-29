# Lógica Completa del Flujo InforMessi

## 🎯 Objetivo Final

Generar y publicar un mensaje diario informativo sobre el Mundial 2026 y la Selección Argentina.

---

## 📋 Flujo Paso a Paso

### 1. Recolección de Datos (`collect-daily-data.py`)

**Qué hace:**
- Obtiene la fecha del día
- Calcula días restantes hasta el Mundial 2026
- Recolecta eventos del día desde:
  - `data/events.json` (eventos manuales)
  - Wikipedia (eventos históricos)
- Recolecta noticias desde:
  - NewsAPI (noticias recientes)
  - RSS feeds (fallback)
  - TyC Sports (scraping, fallback)
- Valida noticias (fecha reciente, contenido relevante)
- Genera sección semanal según el día:
  - Lunes/Viernes: Selección Argentina en Mundiales
  - Martes/Jueves: Jugador de la Scaloneta
  - Miércoles: Sin sección especial
  - Sábado: Dato Mundialista
  - Domingo: Dato País Sede

**Salida:** JSON con todos los datos del día

---

### 2. Generación de Mensaje (`generate-message.py`)

**Qué hace:**
- Lee el JSON de datos del día
- Construye el prompt completo:
  - System prompt (identidad editorial)
  - Main prompt (estructura del mensaje)
  - Datos del día (fecha, eventos, noticias, sección semanal)
  - Ejemplos de mensajes bien formados
- Llama al LLM (Ollama local):
  - Modelo: el que tengas configurado
  - Envía el prompt completo
  - Recibe el mensaje generado
- Valida el mensaje:
  - Longitud (90-130 palabras)
  - Estructura (6 bloques)
  - Frase de cierre ("Coronados de gloria vivamos")

**Salida:** Mensaje de texto listo para revisar

---

### 3. Revisión Humana (`telegram-preview.py`)

**Qué hace:**
- Envía el mensaje a Telegram (chat privado de revisión)
- Agrega botones interactivos:
  - ✅ Aprobar
  - ❌ Rechazar
  - ✏️ Editar
- Espera respuesta del usuario
- Si se aprueba:
  - Publica en canal público de Telegram
  - Confirma publicación
- Si se rechaza:
  - Notifica y termina
- Si se edita:
  - Permite editar manualmente (por ahora)

**Salida:** Mensaje publicado o rechazado

---

## 🔄 Flujo Completo Visual

```
┌─────────────────────────────────┐
│  CRON (8:00 AM diario)          │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  daily-flow.sh                  │
│  (Orquestador principal)        │
└──────────────┬──────────────────┘
               │
               ├─► Paso 1: Recolectar
               │   collect-daily-data.py
               │   └─► fetch-events-enhanced.py
               │   └─► fetch-news.py
               │   └─► generate-weekly-sections.py
               │
               ├─► Paso 2: Generar
               │   generate-message.py
               │   └─► Construir prompt
               │   └─► Llamar LLM (Ollama)
               │   └─► Validar mensaje
               │
               └─► Paso 3: Revisar
                   telegram-preview.py
                   └─► Enviar preview
                   └─► Esperar aprobación
                   └─► Publicar si aprobado
```

---

## 🛠️ Configuración Necesaria

### Variables de Entorno (`.env`):
```
TELEGRAM_BOT_TOKEN=tu_token
TELEGRAM_PREVIEW_CHAT_ID=-123456789
TELEGRAM_PUBLISH_CHAT_ID=-987654321
NEWSAPI_KEY=tu_key (opcional)
```

### Servicios Requeridos:
- ✅ Ollama corriendo (LLM local)
- ✅ Telegram Bot configurado
- ✅ Python venv con dependencias

### Archivos de Datos:
- ✅ `data/events.json` (eventos manuales)
- ✅ `data/players.json` (jugadores para sección semanal)
- ✅ `prompts/*.md` (prompts del LLM)

---

## 🎯 Lo que realmente necesitas automatizar

**Solo esto:**
```bash
# Ejecutar diariamente a las 8:00 AM
cd /ruta/a/InforMessi
source venv/bin/activate
export $(grep -v '^#' .env | grep -v '^$' | xargs)
bash scripts/daily-flow.sh
```

**Eso es todo.** El script ya hace todo el flujo.

---

## 💡 ¿Por qué es tan simple?

Porque el diseño es bueno:
- ✅ Un script orquestador (`daily-flow.sh`)
- ✅ Scripts modulares (cada uno hace una cosa)
- ✅ Sin dependencias complejas
- ✅ Flujo lineal claro

**No necesitas n8n porque ya tienes un "workflow" bien diseñado en bash.**

---

## 📊 Comparación

| Aspecto | Con Cron | Con n8n |
|---------|---------|---------|
| **Complejidad** | ⭐ Simple | ⭐⭐⭐ Complejo |
| **Configuración** | 1 comando | Docker + Webhook + Config |
| **Mantenimiento** | ⭐ Mínimo | ⭐⭐⭐ Alto |
| **Confiabilidad** | ⭐⭐⭐ Alta | ⭐⭐ Media |
| **Para Portfolio** | ⭐⭐ Bueno | ⭐⭐⭐ Muy bueno |
| **Overhead** | Ninguno | Docker + Servicios |

---

**Conclusión: Cron es la mejor opción para tu caso** ✅

