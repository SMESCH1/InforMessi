# n8n Workflows - InforMessi

Este directorio contiene los workflows de n8n para la automatización del pipeline editorial.

## Estructura

```
n8n/
├── workflows/          # Archivos JSON exportados de n8n
└── README.md          # Este archivo
```

## Workflows Principales

### Workflow Diario (por implementar)

El workflow principal ejecutará diariamente:

1. **Trigger**: Cron diario (ej: 8:00 AM hora Argentina)
2. **Recolección de datos**:
   - Clima (AMBA y La Plata)
   - Eventos del día (cumpleaños, partidos, etc.)
   - Noticias relevantes
3. **Generación de mensaje**:
   - Construcción del prompt con datos del día
   - Llamada al LLM (modelo local)
   - Generación del mensaje
4. **Preview**:
   - Envío a Telegram (canal privado de revisión)
   - Espera de aprobación humana
5. **Publicación**:
   - Si se aprueba: publicación en Telegram público
   - Si se rechaza: notificación y fin del workflow

## Cómo Exportar Workflows

1. En n8n, abre el workflow
2. Click en el menú (tres puntos)
3. Selecciona "Download"
4. Guarda el archivo JSON en `workflows/`

## Convenciones de Nombres

- `daily-message-generation.json` - Workflow principal diario
- `manual-trigger.json` - Workflow para pruebas manuales
- `data-collection.json` - Workflow auxiliar de recolección

## Variables de Entorno

Los workflows usarán variables de entorno definidas en `.env`:
- `LLM_BASE_URL`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_PREVIEW_CHAT_ID`
- etc.

## Próximos Pasos

- [ ] Diseñar workflow básico en n8n
- [ ] Exportar workflow a este directorio
- [ ] Documentar nodos y conexiones
- [ ] Configurar triggers y schedules

---

*Los workflows se implementarán en la Fase 2 (MVP con datos mock)*

