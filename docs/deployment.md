# Guía de Despliegue - InforMessi

Esta guía detalla cómo desplegar y configurar el sistema InforMessi.

## Requisitos Previos

### Software Necesario

- **n8n**: Versión 1.0 o superior
- **LLM Local**: Ollama u otro modelo local
- **Telegram Bot**: Bot creado con @BotFather
- **Node.js** (opcional, si se usan scripts)

### Servicios Opcionales

- **API de Clima**: OpenWeatherMap u otro
- **API de Noticias**: Según disponibilidad
- **Notion** (opcional, para revisión humana)

## Configuración Inicial

### 1. Variables de Entorno

Copia `.env.example` a `.env` y completa las variables:

```bash
cp .env.example .env
```

Edita `.env` con tus valores:

```env
# LLM
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
LLM_BASE_URL=http://localhost:11434

# Telegram
TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_publico
TELEGRAM_PREVIEW_CHAT_ID=tu_chat_id_privado

# APIs
WEATHER_API_KEY=tu_api_key
```

### 2. Configurar LLM Local

#### Con Ollama

```bash
# Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Descargar modelo
ollama pull llama3.2

# Verificar que funciona
ollama run llama3.2 "Hola"
```

#### Con Otro Modelo Local

Ajusta `LLM_BASE_URL` y `LLM_MODEL` según tu configuración.

### 3. Configurar Telegram Bot

1. Habla con @BotFather en Telegram
2. Crea un nuevo bot: `/newbot`
3. Guarda el token en `.env` como `TELEGRAM_BOT_TOKEN`
4. Crea un canal privado para preview
5. Obtén el chat ID del canal privado
6. Obtén el chat ID del canal público

### 4. Configurar n8n

1. Instala n8n (Docker recomendado):

```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

2. Accede a `http://localhost:5678`
3. Configura variables de entorno en n8n (Settings > Environment Variables)
4. Importa workflows desde `n8n/workflows/`

## Despliegue

### Desarrollo Local

1. Clona el repositorio
2. Configura `.env`
3. Inicia n8n
4. Inicia LLM local (Ollama)
5. Importa workflows en n8n
6. Configura trigger de prueba

### Producción

#### Opción 1: Servidor Dedicado

- Instala n8n y LLM en servidor
- Configura cron para trigger diario
- Usa systemd o supervisor para servicios
- Configura backup de workflows

#### Opción 2: Docker Compose

```yaml
# docker-compose.yml (ejemplo)
version: '3.8'
services:
  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    volumes:
      - ~/.n8n:/home/node/.n8n
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=password
  
  ollama:
    image: ollama/ollama
    volumes:
      - ollama_data:/root/.ollama
```

#### Opción 3: Cloud (n8n Cloud + LLM Local)

- n8n Cloud para orquestación
- LLM local en servidor propio
- Conectar vía API

## Configuración de Workflows

### Workflow Diario

1. Importa `n8n/workflows/daily-message-generation.json`
2. Configura trigger cron (ej: `0 8 * * *` para 8 AM)
3. Verifica conexiones:
   - LLM node → URL y modelo correctos
   - Telegram nodes → Tokens correctos
4. Prueba con trigger manual

### Workflow de Preview

1. Configura bot de Telegram con botones:
   - "Aprobar"
   - "Rechazar"
   - "Editar"
2. Conecta con workflow principal
3. Prueba flujo completo

## Monitoreo

### Logs

- **n8n**: Logs en interfaz web o archivos
- **LLM**: Logs según implementación
- **Telegram**: Historial en chats

### Alertas

Configura notificaciones para:
- Errores en generación
- Timeouts en revisión humana
- Fallos en publicación

## Mantenimiento

### Backup

- Workflows de n8n (exportar regularmente)
- Archivo `data/events.json`
- Variables de entorno (guardar de forma segura)

### Actualización de Eventos

Edita `data/events.json` con eventos futuros:
- Cumpleaños de jugadores
- Partidos confirmados
- Fechas importantes

### Actualización de Prompts

Los prompts en `prompts/` pueden actualizarse sin redeploy:
- Edita archivos .md
- Reimporta en n8n si es necesario

## Troubleshooting

### LLM no responde

- Verifica que Ollama esté corriendo
- Revisa `LLM_BASE_URL` en .env
- Prueba modelo manualmente

### Telegram no envía

- Verifica token del bot
- Verifica chat IDs
- Revisa permisos del bot en canales

### Workflow falla

- Revisa logs en n8n
- Verifica conexiones entre nodos
- Prueba cada nodo individualmente

## Seguridad

- **Nunca** commitees `.env` al repositorio
- Usa variables de entorno en producción
- Protege acceso a n8n con autenticación
- Limita acceso a canales de Telegram
- Backup de datos sensibles

## Próximos Pasos

- [ ] Documentar workflows específicos
- [ ] Agregar scripts de deployment
- [ ] Crear guía de troubleshooting detallada
- [ ] Documentar integración con APIs reales

---

*Esta guía se actualizará según avance el proyecto*

