# Solución: Error "Unrecognized node type: n8n-nodes-base.executeCommand"

## Problema

El nodo `executeCommand` no está disponible en tu instalación de n8n. Este nodo puede requerir:
- Instalación de un paquete adicional
- Versión específica de n8n
- Configuración especial

## Soluciones

Tienes **3 opciones** para resolver esto:

---

## ✅ Opción 1: Usar Nodo "Code" (Recomendado)

El nodo "Code" está disponible en todas las versiones de n8n y permite ejecutar JavaScript/Node.js.

### Pasos:

1. **Importar workflow alternativo**:
   - En n8n: "Workflows" → "Import from File"
   - Selecciona: `n8n/workflows/daily-informessi-code.json`

2. **Verificar el código**:
   - El workflow usa el nodo "Code" que ejecuta el script directamente
   - No requiere configuración adicional

3. **Probar**:
   - Haz clic en "Execute Workflow"
   - Debería funcionar sin problemas

---

## ✅ Opción 2: Instalar Nodo Execute Command

Si prefieres usar el nodo original:

### Con Docker:

```bash
# Detener n8n
docker stop n8n

# Reiniciar con permisos para ejecutar comandos
docker run -d \
  --name n8n \
  --restart unless-stopped \
  -p 5678:5678 \
  -v ~/n8n-data:/home/node/.n8n \
  -v /home/sebastian-mesch-henriques:/home/sebastian-mesch-henriques \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=tu_password \
  n8nio/n8n
```

**Nota**: Esto monta tu directorio en el contenedor para que pueda ejecutar scripts.

### Con npm:

El nodo `executeCommand` puede requerir instalación manual. Verifica en la documentación de n8n.

---

## ✅ Opción 3: Usar Servidor Webhook (Más robusto)

Crear un servidor webhook que ejecute el script cuando n8n lo llame.

### Pasos:

1. **Iniciar servidor webhook**:
   ```bash
   cd /home/sebastian-mesch-henriques/Escritorio/Personal/InforMessi
   source venv/bin/activate
   python3 scripts/webhook-server.py
   ```

2. **Importar workflow HTTP**:
   - En n8n: "Workflows" → "Import from File"
   - Selecciona: `n8n/workflows/daily-informessi-http.json`

3. **Probar**:
   - El workflow hará una llamada HTTP al servidor
   - El servidor ejecutará el script

### Mantener servidor corriendo:

```bash
# Con systemd (recomendado para producción)
# O usar screen/tmux
screen -S informessi-webhook
python3 scripts/webhook-server.py
# Ctrl+A, D para detach
```

---

## 🎯 Recomendación

**Usa la Opción 1 (Nodo Code)** porque:
- ✅ No requiere configuración adicional
- ✅ Funciona inmediatamente
- ✅ No necesita servicios externos
- ✅ Es la solución más simple

---

## 📋 Workflows Disponibles

1. **`daily-informessi-code.json`** ⭐ (Recomendado)
   - Usa nodo "Code" estándar
   - Funciona sin configuración

2. **`daily-informessi-http.json`**
   - Usa HTTP Request
   - Requiere servidor webhook corriendo

3. **`daily-informessi-simple.json`** (Original)
   - Requiere nodo executeCommand
   - No funciona sin configuración adicional

---

## 🧪 Probar

Después de importar el workflow con nodo "Code":

1. Haz clic en "Execute Workflow"
2. Verifica que el nodo "Ejecutar Flujo InforMessi" se ejecute
3. Revisa los logs del nodo
4. Verifica que el mensaje llegue a Telegram

---

**La Opción 1 es la más rápida y simple** 🚀

