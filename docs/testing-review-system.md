# Guía de Prueba del Sistema de Revisión - InforMessi

Esta guía te ayudará a probar el sistema de revisión humana paso a paso.

## Requisitos Previos

- ✅ Ollama instalado y funcionando
- ✅ Modelo llama3.2 instalado
- ✅ Python 3 con `requests` instalado
- ⚠️ Bot de Telegram configurado (veremos cómo)

## Paso 1: Configurar Bot de Telegram

### 1.1 Crear el Bot

1. Abre Telegram y busca **@BotFather**
2. Envía `/start`
3. Envía `/newbot`
4. Sigue las instrucciones:
   - Nombre: "InforMessi Preview Bot" (o el que prefieras)
   - Username: `informessi_preview_bot` (debe terminar en `bot`)
5. **Copia el token** que te da (ej: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 1.2 Crear Canal/Grupo de Preview

1. Crea un **grupo privado** en Telegram
2. Agrega tu bot al grupo como **administrador**
3. Envía un mensaje al grupo (cualquier cosa, ej: "Hola")

### 1.3 Obtener Chat ID

Ejecuta:

```bash
python3 scripts/get-telegram-chat-id.py --token TU_TOKEN_AQUI
```

**Copia el Chat ID** que aparece (será un número negativo, ej: `-123456789`)

### 1.4 (Opcional) Crear Canal Público

Si querés probar la publicación:

1. Crea un **canal público** en Telegram
2. Agrega tu bot como **administrador**
3. Publica un mensaje
4. Obtén el Chat ID con el mismo script

## Paso 2: Configurar Variables de Entorno

### 2.1 Crear archivo .env

```bash
cd /home/sebastian-mesch-henriques/Escritorio/Personal/InforMessi
cp .env.example .env
```

### 2.2 Editar .env

Abre `.env` y completa:

```env
TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_PREVIEW_CHAT_ID=-123456789
TELEGRAM_PUBLISH_CHAT_ID=-987654321  # Opcional
```

## Paso 3: Probar el Sistema

### Prueba 1: Solo Preview (Sin Esperar Respuesta)

```bash
# Generar un mensaje de prueba
python3 scripts/generate-message.py --data mock-data.json --output /tmp/mensaje-test.txt

# Enviar preview (sin esperar respuesta)
python3 scripts/telegram-preview.py \
  --message "$(cat /tmp/mensaje-test.txt)" \
  --preview-chat-id TU_CHAT_ID \
  --token TU_TOKEN \
  --no-wait
```

**Qué deberías ver:**
- Un mensaje en Telegram con el preview
- Botones: ✅ Aprobar, ❌ Rechazar, ✏️ Editar
- El script termina inmediatamente

### Prueba 2: Preview con Espera de Respuesta

```bash
# Generar mensaje
python3 scripts/generate-message.py --data mock-data.json --output /tmp/mensaje-test.txt

# Enviar y esperar respuesta (timeout: 60 segundos para prueba)
python3 scripts/telegram-preview.py \
  --message "$(cat /tmp/mensaje-test.txt)" \
  --preview-chat-id TU_CHAT_ID \
  --publish-chat-id TU_CANAL_PUBLICO \
  --token TU_TOKEN \
  --timeout 60
```

**Qué hacer:**
1. Verás el preview en Telegram
2. Haz click en uno de los botones:
   - **✅ Aprobar**: El mensaje se publicará automáticamente
   - **❌ Rechazar**: El script terminará sin publicar
   - **✏️ Editar**: El script terminará y podrás editar manualmente

**Qué deberías ver en la terminal:**
- "⏳ Esperando respuesta..."
- Cuando hagas click: "✅ Mensaje aprobado" (o el mensaje correspondiente)
- Si aprobaste: "📤 Publicando en canal..."

### Prueba 3: Flujo Completo Integrado

```bash
# Script que hace todo el flujo
python3 scripts/generate-message.py --data mock-data.json --output /tmp/mensaje.txt && \
python3 scripts/telegram-preview.py \
  --message "$(cat /tmp/mensaje.txt)" \
  --preview-chat-id $TELEGRAM_PREVIEW_CHAT_ID \
  --publish-chat-id $TELEGRAM_PUBLISH_CHAT_ID \
  --timeout 300
```

## Paso 4: Probar Diferentes Escenarios

### Escenario A: Aprobar Mensaje

1. Genera mensaje
2. Envía preview
3. Haz click en "✅ Aprobar"
4. **Resultado esperado**: Mensaje publicado en canal público

### Escenario B: Rechazar Mensaje

1. Genera mensaje
2. Envía preview
3. Haz click en "❌ Rechazar"
4. **Resultado esperado**: Script termina, mensaje NO publicado

### Escenario C: Editar Mensaje

1. Genera mensaje
2. Envía preview
3. Haz click en "✏️ Editar"
4. **Resultado esperado**: Script termina, puedes editar manualmente

### Escenario D: Timeout

1. Genera mensaje
2. Envía preview
3. **NO hagas click** en ningún botón
4. Espera el timeout (60 segundos en la prueba)
5. **Resultado esperado**: Script termina sin publicar

## Troubleshooting

### Error: "Unauthorized"

- Verifica que el token sea correcto
- Asegúrate de copiar el token completo (incluye los dos puntos)

### Error: "Chat not found"

- Verifica que el Chat ID sea correcto
- Asegúrate de que el bot esté agregado al grupo/canal
- Envía un mensaje al grupo antes de obtener el Chat ID

### Los botones no funcionan

- Verifica que el bot tenga permisos de administrador
- Asegúrate de hacer click en los botones (no solo leer el mensaje)
- Verifica que el token sea correcto

### No recibo actualizaciones

- El bot debe estar "iniciado" (envía `/start` al bot en privado)
- Verifica que el bot esté en el grupo/canal
- Asegúrate de haber enviado un mensaje al grupo

### El script se cuelga esperando respuesta

- Usa `Ctrl+C` para cancelar
- Verifica que el bot esté funcionando
- Prueba con `--no-wait` primero para verificar que el preview se envía

## Checklist de Prueba

- [ ] Bot creado y token obtenido
- [ ] Grupo/canal creado y bot agregado
- [ ] Chat ID obtenido correctamente
- [ ] Variables de entorno configuradas
- [ ] Preview se envía correctamente
- [ ] Botones aparecen y funcionan
- [ ] Aprobar funciona y publica
- [ ] Rechazar funciona y no publica
- [ ] Editar funciona
- [ ] Timeout funciona correctamente

## Próximos Pasos

Una vez que el sistema de revisión funcione:

1. Integrar con n8n (Fase 4+)
2. Configurar trigger automático diario
3. Agregar notificaciones adicionales
4. Implementar historial de mensajes

---

*Prueba todos los escenarios antes de avanzar a la siguiente fase*

