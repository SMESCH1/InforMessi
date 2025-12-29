# Flujo de Revisión Explicado - InforMessi

Esta guía explica en detalle cómo funciona el flujo de revisión humana actual y las opciones futuras.

## Estado Actual: Revisión desde Telegram

### ¿Por qué Telegram y no Notion?

**Implementación actual**: Telegram
- ✅ Rápido de implementar
- ✅ Botones interactivos funcionan bien
- ✅ Notificaciones push automáticas
- ✅ Accesible desde móvil y desktop
- ⚠️ Edición limitada (ver abajo)

**Notion (futuro)**:
- ✅ Mejor para edición de texto
- ✅ Historial más completo
- ✅ Mejor para colaboración
- ⚠️ Requiere más configuración
- ⚠️ API más compleja

### Flujo Actual Detallado

```
1. Mensaje Generado
   ↓
2. Preview en Telegram (canal privado)
   - Mensaje completo visible
   - Botones: ✅ Aprobar | ❌ Rechazar | ✏️ Editar
   ↓
3. Revisor decide:
   
   A) ✅ APROBAR
      → Script publica automáticamente
      → Fin del flujo
   
   B) ❌ RECHAZAR
      → Script termina
      → Mensaje NO se publica
      → Fin del flujo
   
   C) ✏️ EDITAR
      → Script termina
      → Revisor edita manualmente
      → Revisor publica manualmente o reenvía
```

## ¿Cómo Editar un Mensaje Actualmente?

### Opción 1: Edición Manual en Telegram

1. Click en "✏️ Editar" en el preview
2. El script termina
3. **Copiar** el texto del mensaje del preview
4. **Editar** el texto (en Telegram, en un editor de texto, etc.)
5. **Publicar manualmente**:
   - Copiar el texto editado
   - Enviarlo al canal público manualmente
   - O usar el script de publicación con el texto editado

### Opción 2: Reenvío para Aprobación

1. Click en "✏️ Editar"
2. Editar el mensaje
3. Guardar el mensaje editado en un archivo
4. Reenviar para aprobación:
   ```bash
   python3 scripts/telegram-preview.py \
     --message "$(cat mensaje-editado.txt)" \
     --preview-chat-id $TELEGRAM_PREVIEW_CHAT_ID \
     --publish-chat-id $TELEGRAM_PUBLISH_CHAT_ID
   ```

### Opción 3: Edición con Script Auxiliar (Futuro)

Se podría crear un script que:
1. Recibe el mensaje original
2. Permite edición en un editor de texto
3. Reenvía automáticamente para aprobación

## Limitaciones Actuales

### Edición en Telegram

- ❌ **No se puede editar inline** desde el bot
- ❌ **No hay editor integrado** en el preview
- ✅ **Solución actual**: Edición manual externa

### Notion (Futuro)

La integración con Notion resolvería:
- ✅ Edición inline cómoda
- ✅ Historial completo de cambios
- ✅ Mejor para textos largos
- ✅ Colaboración con múltiples revisores

## Flujo Ideal Futuro (Con Notion)

```
1. Mensaje Generado
   ↓
2. Crear página en Notion
   - Mensaje editable inline
   - Botones de acción
   - Historial de cambios
   ↓
3. Revisor edita directamente en Notion
   ↓
4. Click en "✅ Aprobar"
   → Publicar automáticamente
```

## Comparación: Telegram vs Notion

| Característica | Telegram (Actual) | Notion (Futuro) |
|----------------|-------------------|-----------------|
| **Edición** | Manual externa | Inline en Notion |
| **Velocidad** | Rápido | Medio |
| **Notificaciones** | Push automáticas | Push opcionales |
| **Historial** | Limitado | Completo |
| **Colaboración** | Básica | Avanzada |
| **Complejidad** | Baja | Media |
| **Móvil** | Excelente | Buena |

## Recomendación

**Para empezar**: Telegram es suficiente y funciona bien.

**Para escalar**: Notion sería mejor si:
- Necesitas editar frecuentemente
- Trabajas con múltiples revisores
- Quieres historial detallado
- Prefieres una interfaz más rica

## Próximos Pasos

1. **Ahora**: Usar Telegram para revisión (ya implementado)
2. **Futuro**: Evaluar Notion si la edición manual se vuelve problemática
3. **Mejora intermedia**: Crear script auxiliar para facilitar edición

---

*El flujo actual funciona bien para la mayoría de casos. Notion sería una mejora, no un requisito.*

