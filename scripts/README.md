# Scripts Auxiliares - InforMessi

Este directorio contiene scripts auxiliares que pueden ser necesarios para el funcionamiento del sistema.

## Scripts Disponibles

### `generate-message.py`

Script de prueba para generar mensajes con LLM local (Ollama).

### `telegram-preview.py`

Script para enviar mensajes a Telegram para revisión humana.

#### Requisitos

```bash
pip install requests
```

#### Uso Básico

```bash
python3 scripts/telegram-preview.py \
  --message "$(cat mensaje.txt)" \
  --preview-chat-id TU_CHAT_ID \
  --token TU_TOKEN
```

#### Opciones

```bash
python3 scripts/telegram-preview.py \
  --message "Texto del mensaje" \
  --message-id "unique-id" \
  --preview-chat-id -123456789 \
  --publish-chat-id -987654321 \
  --token TU_TOKEN \
  --timeout 3600 \
  --no-wait
```

#### Parámetros

- `--message`: Texto del mensaje a revisar (requerido)
- `--message-id`: ID único del mensaje (opcional, default: timestamp)
- `--preview-chat-id`: Chat ID del canal de preview (requerido)
- `--publish-chat-id`: Chat ID del canal público (opcional)
- `--token`: Token del bot de Telegram (o usar TELEGRAM_BOT_TOKEN)
- `--timeout`: Timeout en segundos (default: 3600)
- `--no-wait`: Solo enviar preview, no esperar respuesta

#### Ejemplos

```bash
# Enviar para revisión y esperar respuesta
python3 scripts/telegram-preview.py \
  --message "$(cat mensaje.txt)" \
  --preview-chat-id $TELEGRAM_PREVIEW_CHAT_ID \
  --publish-chat-id $TELEGRAM_PUBLISH_CHAT_ID

# Solo enviar preview sin esperar
python3 scripts/telegram-preview.py \
  --message "$(cat mensaje.txt)" \
  --preview-chat-id $TELEGRAM_PREVIEW_CHAT_ID \
  --no-wait
```

### `get-telegram-chat-id.py`

Script auxiliar para obtener Chat IDs de Telegram.

#### Uso

```bash
python3 scripts/get-telegram-chat-id.py --token TU_TOKEN
```

#### Instrucciones

1. Agrega el bot al grupo/canal
2. Envía un mensaje al grupo/canal
3. Ejecuta el script
4. Copia el Chat ID que aparece

### `demo-mvp.py`

Script de demostración que muestra cómo se construye el prompt (sin necesidad de Ollama).

#### Uso

```bash
python3 scripts/demo-mvp.py --data mock-data.json
```

### `generate-message.py`

Script de prueba para generar mensajes con LLM local (Ollama).

#### Requisitos

```bash
pip install requests
```

#### Uso Básico

```bash
python scripts/generate-message.py
```

#### Opciones

```bash
python scripts/generate-message.py \
  --data mock-data.json \
  --model llama3.2 \
  --base-url http://localhost:11434 \
  --output mensaje-generado.txt
```

#### Parámetros

- `--data`: Archivo de datos mock a usar (default: `mock-data.json`)
- `--model`: Modelo de Ollama a usar (default: `llama3.2`)
- `--base-url`: URL base de Ollama (default: `http://localhost:11434`)
- `--output`: Archivo donde guardar el mensaje generado (opcional)

#### Ejemplos

```bash
# Usar datos mock con evento importante
python scripts/generate-message.py --data mock-data.json

# Usar datos mock sin evento
python scripts/generate-message.py --data mock-data-no-event.json

# Usar datos mock con partido
python scripts/generate-message.py --data mock-data-match.json

# Guardar resultado en archivo
python scripts/generate-message.py --output mensaje.txt
```

#### Datos Mock Disponibles

- `mock-data.json`: Día con cumpleaños de Messi
- `mock-data-no-event.json`: Día sin evento importante
- `mock-data-match.json`: Día con partido de la selección

## Propósito

Los scripts aquí pueden servir para:

- Procesamiento de datos
- Utilidades de formato
- Validación de contenido
- Testing y debugging
- Tareas de mantenimiento

## Estructura

```
scripts/
├── README.md          # Este archivo
├── generate-message.py # Generador de mensajes (MVP)
└── [otros scripts según necesidad]
```

## Nota sobre Tecnología

El proyecto es flexible en cuanto a tecnología. Los scripts pueden estar en:
- Python
- Node.js
- Bash
- O cualquier lenguaje que sea necesario

## Cuándo Usar Scripts

Usa scripts cuando:
- n8n no puede hacer algo directamente
- Necesitas procesamiento complejo de datos
- Requieres validaciones específicas
- Necesitas herramientas de línea de comandos
- Quieres probar componentes antes de integrarlos

## Cuándo NO Usar Scripts

Evita scripts cuando:
- n8n puede hacerlo directamente
- Agrega complejidad innecesaria
- Puede resolverse con configuración

## Próximos Pasos

Los scripts se crearán según necesidad durante el desarrollo.

---

*Mantener este directorio simple y solo agregar scripts cuando sean realmente necesarios*
