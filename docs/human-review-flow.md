# Flujo de Revisión Humana - InforMessi

Esta guía detalla cómo funciona el sistema de revisión humana (Human in the Loop) en InforMessi.

## Visión General

El sistema de revisión humana garantiza que **todos los mensajes** sean revisados por un humano antes de publicarse. Esto es crítico para:

- Mantener calidad editorial
- Prevenir errores o datos inventados
- Ajustar contenido según contexto
- Mantener responsabilidad sobre lo publicado

## Flujo Completo

```
┌─────────────────┐
│ Mensaje         │
│ Generado        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Envío Preview   │
│ (Telegram)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Espera          │
│ Respuesta       │
└────────┬────────┘
         │
         ▼
    ┌────┴────┐
    │         │         │
    ▼         ▼         ▼
┌──────┐ ┌──────┐ ┌──────┐
│Aprobar│ │Rechazar│ │Editar│
└──┬───┘ └──┬───┘ └──┬───┘
   │        │        │
   ▼        ▼        ▼
┌──────┐ ┌──────┐ ┌──────┐
│Publicar│ │Fin   │ │Editar│
│        │ │      │ │Manual│
└────────┘ └──────┘ └──┬───┘
                       │
                       ▼
                  ┌────────┐
                  │Publicar│
                  └────────┘
```

## Componentes

### 1. Preview en Telegram (Implementación Actual)

**Estado**: ✅ Implementado

El mensaje generado se envía a un canal/grupo privado de Telegram con:

- **Texto completo** del mensaje
- **ID único** del mensaje
- **Botones de acción**:
  - ✅ Aprobar
  - ❌ Rechazar
  - ✏️ Editar

**Nota**: La revisión actual se hace desde Telegram. La opción de Notion está planificada para el futuro (ver `docs/future-features.md`).

### 2. Espera de Respuesta

El sistema espera la respuesta del revisor:

- **Timeout**: Configurable (default: 1 hora)
- **Formato**: Botones inline de Telegram
- **Feedback**: Confirmación visual al hacer click

### 3. Acciones Disponibles

#### ✅ Aprobar

- El mensaje se publica automáticamente
- No requiere edición adicional
- Se envía al canal público configurado

#### ❌ Rechazar

- El mensaje NO se publica
- El workflow termina
- Se puede generar un nuevo mensaje si es necesario

#### ✏️ Editar

**Flujo actual (Telegram)**:
- El script termina y marca el mensaje para edición
- El revisor debe **editar manualmente** el mensaje en Telegram
- Luego debe **publicar manualmente** o copiar el mensaje editado y reenviarlo para aprobación

**Limitación actual**: Telegram no permite edición inline desde el bot. El flujo es:
1. Click en "✏️ Editar" → Script termina
2. Revisor copia el mensaje del preview
3. Revisor edita el mensaje (en Telegram o en otro editor)
4. Revisor publica manualmente o reenvía el mensaje editado para aprobación

**Mejora futura**: Integración con Notion permitiría edición inline más cómoda (ver `docs/future-features.md`).

## Implementación

### Script de Preview

```bash
python3 scripts/telegram-preview.py \
  --message "$(cat mensaje.txt)" \
  --preview-chat-id -123456789 \
  --publish-chat-id -987654321 \
  --token TU_TOKEN
```

### Integración con Generación

```bash
# Generar mensaje
python3 scripts/generate-message.py --data mock-data.json --output /tmp/mensaje.txt

# Enviar para revisión
python3 scripts/telegram-preview.py \
  --message "$(cat /tmp/mensaje.txt)" \
  --preview-chat-id $TELEGRAM_PREVIEW_CHAT_ID \
  --publish-chat-id $TELEGRAM_PUBLISH_CHAT_ID
```

### Modo Sin Espera

Para solo enviar el preview sin esperar respuesta:

```bash
python3 scripts/telegram-preview.py \
  --message "$(cat mensaje.txt)" \
  --preview-chat-id -123456789 \
  --no-wait
```

## Configuración

### Variables de Entorno

```env
TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_PREVIEW_CHAT_ID=-123456789
TELEGRAM_PUBLISH_CHAT_ID=-987654321
```

### Permisos del Bot

El bot necesita:

- **En canal de preview**: Permisos de administrador
- **En canal público**: Permisos de administrador
- **Permisos**: Enviar mensajes, usar botones inline

## Casos de Uso

### Caso 1: Mensaje Aprobado Directamente

1. Sistema genera mensaje
2. Se envía preview
3. Revisor hace click en "✅ Aprobar"
4. Mensaje se publica automáticamente

### Caso 2: Mensaje Requiere Edición

1. Sistema genera mensaje
2. Se envía preview
3. Revisor hace click en "✏️ Editar"
4. Revisor edita el mensaje en Telegram
5. Revisor publica manualmente o reenvía

### Caso 3: Mensaje Rechazado

1. Sistema genera mensaje
2. Se envía preview
3. Revisor hace click en "❌ Rechazar"
4. Workflow termina
5. Se puede generar nuevo mensaje si es necesario

### Caso 4: Timeout

1. Sistema genera mensaje
2. Se envía preview
3. No se recibe respuesta en el timeout
4. Workflow termina sin publicar
5. Revisor puede actuar manualmente después

## Integración con n8n

En n8n, el flujo sería:

1. **Nodo**: Generar mensaje (LLM)
2. **Nodo**: Enviar preview (Telegram)
3. **Nodo**: Esperar respuesta (Webhook o polling)
4. **Nodo**: Decisión (Switch)
   - Si aprobado → Publicar
   - Si rechazado → Notificar y terminar
   - Si editado → Esperar publicación manual

## Mejoras Futuras

- [ ] Notificaciones push si no hay respuesta
- [ ] Historial de mensajes revisados
- [ ] Estadísticas de aprobación/rechazo
- [ ] Edición inline en Telegram
- [ ] Múltiples revisores con votación
- [ ] Integración con Notion para edición

## Seguridad

- **Canal privado**: Solo accesible para revisores autorizados
- **Tokens seguros**: Nunca exponer tokens públicamente
- **Validación**: Verificar que las respuestas sean del revisor autorizado
- **Logs**: Registrar todas las acciones de revisión

---

*El sistema de revisión humana es crítico para mantener la calidad editorial del proyecto*

