# Configuración de Telegram Bot - InforMessi

Esta guía explica cómo configurar el bot de Telegram para el sistema de revisión humana.

## Paso 1: Crear el Bot

1. Abre Telegram y busca **@BotFather**
2. Inicia una conversación y envía `/start`
3. Crea un nuevo bot con `/newbot`
4. Sigue las instrucciones:
   - Elige un nombre para tu bot (ej: "InforMessi Preview Bot")
   - Elige un username (debe terminar en `bot`, ej: `informessi_preview_bot`)
5. **Guarda el token** que te da BotFather (ej: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Paso 2: Obtener Chat IDs

### Chat ID del Canal de Preview (Privado)

1. Crea un grupo o canal privado en Telegram
2. Agrega tu bot al grupo/canal como administrador
3. Envía un mensaje al grupo/canal
4. Visita: `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Reemplaza `<TOKEN>` con el token de tu bot
5. Busca el campo `"chat":{"id":-123456789}` en la respuesta
6. **Guarda ese número** (puede ser negativo para grupos)

**Alternativa con script:**

```bash
# Usa este script para obtener el chat ID
python3 scripts/get-telegram-chat-id.py --token TU_TOKEN
```

### Chat ID del Canal Público (Opcional)

1. Crea un canal público en Telegram
2. Agrega tu bot como administrador
3. Publica un mensaje en el canal
4. Usa el mismo método anterior para obtener el chat ID
   - Para canales públicos, el ID suele ser negativo y empieza con `-100`

## Paso 3: Configurar Variables de Entorno

Edita tu archivo `.env`:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_PREVIEW_CHAT_ID=-123456789
TELEGRAM_PUBLISH_CHAT_ID=-987654321
```

## Paso 4: Probar el Bot

### Prueba Básica

```bash
# Enviar un mensaje de prueba
python3 scripts/telegram-preview.py \
  --message "Mensaje de prueba" \
  --preview-chat-id TU_CHAT_ID \
  --token TU_TOKEN \
  --no-wait
```

### Prueba Completa con Revisión

```bash
# Generar mensaje y enviar para revisión
python3 scripts/generate-message.py --data mock-data.json --output /tmp/mensaje.txt

# Enviar para revisión
python3 scripts/telegram-preview.py \
  --message "$(cat /tmp/mensaje.txt)" \
  --preview-chat-id TU_CHAT_ID \
  --publish-chat-id TU_CANAL_PUBLICO \
  --token TU_TOKEN
```

## Paso 5: Permisos del Bot

Asegúrate de que el bot tenga estos permisos:

- **En el canal de preview**: Administrador con permisos para enviar mensajes
- **En el canal público**: Administrador con permisos para enviar mensajes

## Troubleshooting

### Error: "Unauthorized"

- Verifica que el token sea correcto
- Asegúrate de que el bot esté activo

### Error: "Chat not found"

- Verifica que el chat ID sea correcto
- Asegúrate de que el bot esté agregado al grupo/canal
- Para grupos, el bot debe haber recibido al menos un mensaje

### Los botones no funcionan

- Verifica que el bot tenga permisos de administrador
- Asegúrate de que el script esté usando el token correcto

### No recibo actualizaciones

- El bot debe estar "iniciado" (envía `/start` al bot)
- Verifica que el chat ID sea correcto
- Asegúrate de que el bot esté en el grupo/canal

## Integración con n8n

Para usar en n8n:

1. Configura las variables de entorno en n8n
2. Usa el nodo "Telegram" de n8n
3. O usa el nodo "HTTP Request" para llamar a la API de Telegram directamente

## Seguridad

- **Nunca** compartas tu token públicamente
- **Nunca** commitees el archivo `.env` al repositorio
- Usa variables de entorno en producción
- Considera usar un bot separado para preview y publicación

---

*Una vez configurado, el bot estará listo para recibir mensajes para revisión*

