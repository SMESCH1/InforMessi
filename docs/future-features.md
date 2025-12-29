# Features Futuras - InforMessi

Este documento lista features deseables para implementar en el futuro, una vez que el sistema base esté funcionando correctamente.

## Integración con WhatsApp (whatsmeow)

### Descripción

Integración con WhatsApp usando [whatsmeow](https://github.com/tulir/whatsmeow) para publicar mensajes además de Telegram.

### Motivación

- Ampliar el alcance del contenido
- Llegar a audiencias que prefieren WhatsApp
- Publicación multi-canal automática

### Consideraciones Importantes

⚠️ **Uso de teléfono prepago**: Se recomienda usar un **teléfono prepago dedicado** para esta integración, NO el número personal, para evitar riesgos de bloqueo o problemas con la cuenta personal de WhatsApp.

### Implementación Propuesta

#### Tecnología

- **whatsmeow**: Librería Go para WhatsApp web multidevice API (https://github.com/tulir/whatsmeow)
- **Self-hosted**: Ejecutar en servidor propio
- **Go**: Servicio HTTP wrapper o integración directa

#### Opciones de Implementación

**Opción A: Servicio HTTP Wrapper (Recomendado)**
- Crear un servicio HTTP en Go que use whatsmeow
- Exponer API REST para integración
- Integrar desde Python/scripts existentes vía HTTP

**Opción B: Integración Directa**
- Usar whatsmeow directamente desde Go
- Crear scripts en Go para publicación
- Mantener Python para el resto del sistema

#### Componentes Necesarios

1. **Servicio WhatsApp**: Servicio HTTP wrapper usando whatsmeow (Opción A) o scripts Go (Opción B)
2. **Publicador multi-canal**: Extender sistema actual para soportar Telegram + WhatsApp
3. **Configuración**: Variables de entorno para WhatsApp
4. **Integración con revisión**: Al aprobar, publicar en ambos canales

#### Estructura Propuesta

**Opción A (HTTP Wrapper)**:
```
scripts/
├── publish-message.py          # Publicador multi-canal
│   ├── TelegramBot (existente)
│   ├── WhatsAppClient (nuevo, HTTP)
│   └── MultiChannelPublisher (nuevo)

services/
└── whatsapp-service/            # Servicio Go con whatsmeow
    ├── main.go
    └── go.mod
```

**Opción B (Directo)**:
```
scripts/
├── publish-message.py          # Publicador multi-canal
│   └── TelegramBot (existente)

scripts/go/
└── publish-whatsapp.go         # Script Go con whatsmeow
```

#### Variables de Entorno

```env
# WhatsApp (whatsmeow) - FUTURO
WHATSAPP_SERVICE_URL=http://localhost:8080  # Si Opción A
WHATSAPP_CHAT_ID=5491123456789@c.us
WHATSAPP_SESSION_PATH=/path/to/session      # Para almacenar sesión
```

#### Flujo Propuesto

1. Mensaje generado
2. Preview en Telegram (revisión humana)
3. Al aprobar → Publicar en:
   - Telegram (canal público)
   - WhatsApp (grupo/canal configurado)

### Pasos para Implementación Futura

1. **Instalar Go** (si no está instalado):
   ```bash
   # Verificar versión
   go version
   ```

2. **Instalar whatsmeow**:
   ```bash
   go get go.mau.fi/whatsmeow
   ```

3. **Crear servicio wrapper o script**:
   - **Opción A**: Servicio HTTP que expone API REST
   - **Opción B**: Script Go directo para publicación

4. **Conectar número prepago**:
   - Generar QR code con whatsmeow
   - Escanear QR con el teléfono prepago
   - Almacenar sesión para reconexión automática

5. **Obtener Chat ID**:
   - Usar whatsmeow para listar chats/grupos
   - Configurar Chat ID del grupo/canal destino

6. **Implementar integración**:
   - Crear cliente WhatsApp (HTTP o directo)
   - Extender publicador multi-canal
   - Integrar con flujo de aprobación

7. **Probar**:
   - Probar envío de mensajes
   - Verificar publicación automática
   - Validar funcionamiento con revisión humana

### Características de whatsmeow

Según la [documentación oficial](https://github.com/tulir/whatsmeow):

✅ **Implementado**:
- Envío de mensajes (texto y media)
- Recepción de mensajes
- Gestión de grupos
- Recepción de eventos de grupos
- Unirse mediante invitaciones
- Notificaciones de escritura
- Recepción de confirmaciones de entrega y lectura
- Estado de la app (contactos, pines, silencios)
- Mensajes de estado (experimental)

❌ **No implementado**:
- Broadcast lists (no soportado en WhatsApp web)
- Llamadas

### Recursos

- [whatsmeow GitHub](https://github.com/tulir/whatsmeow)
- [whatsmeow GoDoc](https://pkg.go.dev/go.mau.fi/whatsmeow)
- [Matrix Room](https://matrix.to/#/#whatsmeow:maunium.net) - Para discusiones
- [WhatsApp Protocol Q&A](https://github.com/tulir/whatsmeow/discussions) - En GitHub

### Estado

- **Prioridad**: Media
- **Dependencias**: Sistema base funcionando correctamente
- **Estimación**: 2-3 días de desarrollo (más que WAHA por necesidad de wrapper/servicio)
- **Riesgos**: Bloqueo de WhatsApp (mitigado con teléfono prepago)
- **Ventaja sobre WAHA**: Librería más directa, sin dependencia de Docker para el servicio HTTP

---

## Integración con Notion para Revisión

### Descripción

Usar Notion como alternativa a Telegram para la revisión humana de mensajes.

### Motivación

- Interfaz más rica para edición
- Mejor historial de mensajes
- Colaboración con múltiples revisores
- Edición inline más cómoda

### Implementación Propuesta

#### Componentes

1. **Notion Database**: Base de datos para mensajes pendientes
2. **Notion API**: Integración con API oficial
3. **Webhook**: Para recibir actualizaciones de Notion
4. **Editor**: Interfaz de edición en Notion

#### Flujo Propuesto

1. Mensaje generado → Crear página en Notion
2. Revisor edita directamente en Notion
3. Botón "Aprobar" en Notion → Publicar
4. Botón "Rechazar" en Notion → Marcar como rechazado

### Estado

- **Prioridad**: Baja
- **Dependencias**: Sistema base funcionando
- **Estimación**: 2-3 días de desarrollo

---

## Otras Features Futuras

### Visuales Automáticas

- Generación automática de imágenes con IA
- Selección inteligente de memes según contenido
- Banco de imágenes curado

### Análisis y Métricas

- Tracking de engagement
- Estadísticas de aprobación/rechazo
- Análisis de contenido generado

### Multi-idioma

- Soporte para otros idiomas
- Traducción automática (opcional)

### Integración con Redes Sociales

- Publicación automática en X (Twitter)
- Publicación en Instagram
- Adaptación de formato por plataforma

---

*Estas features se implementarán según prioridad y necesidad del proyecto*

