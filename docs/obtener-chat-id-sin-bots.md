# Obtener Chat ID sin Bots - InforMessi

Guía para obtener Chat IDs cuando los bots no funcionan.

## 🔧 Método 1: Desde la URL de Telegram

### En Telegram Desktop:

1. Abre Telegram Desktop
2. Ve al grupo/canal
3. Click derecho en el grupo → **"Copy link"** o **"Copiar enlace"**
4. O desde el navegador, copia la URL completa
5. Usa el script:
   ```bash
   python3 scripts/get-chat-id-from-url.py
   ```
6. Pega la URL cuando te lo pida

### En Telegram Web:

1. Abre https://web.telegram.org
2. Ve al grupo
3. Copia la URL del navegador (debería ser algo como `https://web.telegram.org/k/#-1001234567890`)
4. El Chat ID está en la URL después de `#`

## 🔧 Método 2: Revisar Logs de Render

Cuando el bot recibe un mensaje, el webhook lo registra:

1. Envía un mensaje al bot en el grupo
2. Ve a Render → Tu servicio → **Logs**
3. Busca `chat_id` en los logs
4. El Chat ID aparecerá en el log del webhook

## 🔧 Método 3: Eliminar Webhook Temporalmente

Si necesitas usar `getUpdates`:

```bash
# 1. Eliminar webhook
python3 scripts/setup-webhook.py --remove

# 2. Envía un mensaje al bot en el grupo

# 3. Obtener Chat IDs
python3 scripts/get-telegram-chat-id.py

# 4. Restaurar webhook
python3 scripts/setup-webhook.py --webhook-url https://informessi-webhook.onrender.com
```

## 🔧 Método 4: Desde el Código del Bot

Si tienes acceso al código del bot, puedes agregar un comando temporal:

```python
@bot.message_handler(commands=['getchatid'])
def get_chat_id(message):
    chat_id = message.chat.id
    bot.reply_to(message, f"Chat ID: {chat_id}")
```

Luego envía `/getchatid` al bot en el grupo.

## 📝 Notas

- **Grupos**: Chat ID es negativo (ej: `-1001234567890`)
- **Chats privados**: Chat ID es positivo (ej: `123456789`)
- **No incluyas espacios** al copiar el Chat ID
- Los valores de ejemplo en la documentación son solo ejemplos, no credenciales reales

---

**Una vez que tengas el Chat ID, actualízalo usando:**
```bash
python3 scripts/update-chat-ids.py --public-chat-id NUEVO_ID
```

