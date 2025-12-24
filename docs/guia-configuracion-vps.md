# Guía Paso a Paso: Configuración de VPS para InforMessi

Guía detallada para configurar un VPS desde cero para InforMessi.

## 🎯 Objetivo

Configurar un VPS que:
- Ejecute InforMessi cuando la PC local no esté disponible
- Reciba heartbeats de la PC local
- Tenga Ollama corriendo para generar mensajes

---

## 📦 Paso 1: Elegir y Crear VPS

### Opción A: AWS EC2 Free Tier (Recomendado)

**Ver guía completa:** `docs/guia-configuracion-aws.md`

**Resumen rápido:**
1. Crear cuenta en AWS
2. Configurar protección contra cargos (Budgets y alertas)
3. Lanzar instancia EC2 t2.micro (Free tier)
4. Configurar Security Group (puertos 22 y 8080)
5. Conectar por SSH

**⚠️ IMPORTANTE:** Configura alertas de facturación ANTES de crear recursos.

### Opción B: Oracle Cloud Free Tier

1. **Crear cuenta:**
   - Ve a https://cloud.oracle.com
   - Crea cuenta gratuita (requiere tarjeta, pero no se cobra si usas solo free tier)
   - Verifica email

2. **Crear instancia:**
   - Dashboard → "Create a VM instance"
   - Name: `informessi-vps`
   - Image: Ubuntu 22.04
   - Shape: VM.Standard.A1.Flex (Always Free)
   - Configure networking: Dejar por defecto
   - Add SSH keys: Sube tu clave pública SSH
   - Create

3. **Anotar IP pública:**
   - Copia la IP pública que aparece en el dashboard
   - Ejemplo: `123.45.67.89`

### Opción C: Hetzner Cloud (Mejor rendimiento, $5/mes)

1. **Crear cuenta:**
   - Ve a https://www.hetzner.com/cloud
   - Crea cuenta
   - Verifica email

2. **Crear servidor:**
   - "Add Server"
   - Location: Cualquiera (Frankfurt, Nuremberg, etc.)
   - Image: Ubuntu 22.04
   - Type: CX11 (2 vCPU, 4 GB RAM) - $5/mes
   - SSH Keys: Agrega tu clave pública
   - Create

3. **Anotar IP pública**

---

## 🔐 Paso 2: Conectar al VPS

### Desde Linux/Mac:

```bash
# Conectar
ssh ubuntu@TU_VPS_IP
# O si usas root
ssh root@TU_VPS_IP

# Si te pide contraseña y configuraste SSH key, debería conectarse automáticamente
```

### Desde Windows:

Usa PuTTY o WSL (Windows Subsystem for Linux).

**Primera vez que conectas:**
- Te pedirá confirmar fingerprint: escribe `yes`
- Si todo está bien, deberías ver el prompt del servidor

---

## 🛠️ Paso 3: Configurar Sistema Base

### Actualizar sistema:

```bash
sudo apt update
sudo apt upgrade -y
```

### Instalar herramientas básicas:

```bash
sudo apt install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    ufw
```

---

## 🐳 Paso 4: Instalar Docker

### Instalar Docker:

```bash
# Descargar script de instalación
curl -fsSL https://get.docker.com -o get-docker.sh

# Ejecutar instalación
sudo sh get-docker.sh

# Verificar instalación
docker --version
```

### Instalar Docker Compose:

```bash
# Instalar Docker Compose
sudo apt install -y docker-compose

# O usar la versión más reciente
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar
docker-compose --version
```

### Configurar usuario:

```bash
# Agregar usuario actual al grupo docker
sudo usermod -aG docker $USER

# Cerrar sesión y volver a entrar para que tome efecto
exit
# Luego reconectar con ssh
```

### Verificar Docker:

```bash
# Debería funcionar sin sudo
docker ps
docker-compose --version
```

---

## 🔥 Paso 5: Configurar Firewall

```bash
# Permitir SSH (importante, no cerrar esta conexión)
sudo ufw allow 22/tcp

# Permitir puerto de heartbeat
sudo ufw allow 8080/tcp

# Activar firewall
sudo ufw enable

# Verificar reglas
sudo ufw status
```

**⚠️ IMPORTANTE:** No cierres la conexión SSH hasta verificar que todo funciona.

---

## 📥 Paso 6: Subir Código de InforMessi

### Opción A: Clonar desde Git (si tienes repo):

```bash
# Instalar Git si no está
sudo apt install -y git

# Crear directorio
sudo mkdir -p /opt/informessi
sudo chown -R $USER:$USER /opt/informessi

# Clonar repositorio
cd /opt
git clone <TU_REPO_URL> informessi
cd informessi
```

### Opción B: Subir archivos manualmente (desde tu PC local):

```bash
# En tu PC local, comprimir el proyecto
cd /home/sebastian-mesch-henriques/Escritorio/Personal
tar -czf informessi.tar.gz InforMessi/

# Subir al VPS
scp informessi.tar.gz ubuntu@TU_VPS_IP:/tmp/

# En el VPS, descomprimir
ssh ubuntu@TU_VPS_IP
cd /opt
sudo mkdir informessi
sudo chown -R $USER:$USER informessi
cd informessi
tar -xzf /tmp/informessi.tar.gz --strip-components=1
```

---

## ⚙️ Paso 7: Configurar Variables de Entorno

```bash
cd /opt/informessi

# Crear .env desde ejemplo
cp .env.example .env

# Editar .env
nano .env
```

**Agregar estas variables:**

```env
# Heartbeat
VPS_HEARTBEAT_URL=http://localhost:8080
PC_ID=pc-sebastian

# Telegram (mismo token que en PC local)
TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_PREVIEW_CHAT_ID=tu_chat_id_privado
TELEGRAM_PUBLISH_CHAT_ID=tu_chat_id_publico

# LLM
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2

# APIs (opcionales)
NEWSAPI_KEY=tu_key_si_la_tienes
```

**Guardar:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

## 🚀 Paso 8: Construir e Iniciar Servicios

```bash
cd /opt/informessi

# Construir imágenes Docker
docker-compose build

# Iniciar servicios
docker-compose up -d

# Verificar que están corriendo
docker-compose ps
```

**Deberías ver:**
```
NAME                STATUS
ollama              Up
informessi          Up
heartbeat-server    Up
```

---

## 📦 Paso 9: Descargar Modelo de Ollama

```bash
# Entrar al contenedor de Ollama
docker-compose exec ollama ollama pull llama3.2

# Esto puede tardar varios minutos (el modelo es ~2GB)
# Ver progreso en los logs
docker-compose logs -f ollama
```

**Verificar:**
```bash
docker-compose exec ollama ollama list
```

**Deberías ver:**
```
NAME            ID              SIZE    MODIFIED
llama3.2        abc123...        2.0GB   2 hours ago
```

---

## ✅ Paso 10: Verificar Servicios

### Verificar heartbeat server:

```bash
# Verificar estado
curl http://localhost:8080/status

# Debería responder:
# {"status":"ok","registered_pcs":[],"total_pcs":0}
```

### Verificar Ollama:

```bash
# Probar modelo
docker-compose exec ollama ollama run llama3.2 "Hola, ¿cómo estás?"
```

### Ver logs:

```bash
# Todos los servicios
docker-compose logs -f

# Servicio específico
docker-compose logs -f heartbeat-server
docker-compose logs -f ollama
```

---

## ⏰ Paso 11: Configurar Cron

```bash
# Editar crontab
crontab -e

# Si es primera vez, elegir editor (nano es más fácil)
```

**Agregar esta línea:**

```cron
# Ejecutar InforMessi diariamente a las 8:00 AM
# Verifica si PC local está disponible antes de ejecutar
0 8 * * * cd /opt/informessi && docker-compose exec -T informessi python3 scripts/check-pc-available.py > /dev/null 2>&1 || docker-compose exec -T informessi bash scripts/daily-flow-hybrid.sh >> ~/informessi-logs/cron-$(date +\%Y-\%m-\%d).log 2>&1
```

**Guardar:** `Ctrl+O`, `Enter`, `Ctrl+X`

**Crear directorio de logs:**
```bash
mkdir -p ~/informessi-logs
```

**Verificar crontab:**
```bash
crontab -l
```

---

## 🧪 Paso 12: Probar Flujo Completo

### Probar verificación de PC:

```bash
cd /opt/informessi
docker-compose exec informessi python3 scripts/check-pc-available.py
```

**Si PC no está disponible, debería decir:**
```
⚠️  PC local (pc-sebastian) NO está disponible
   Razón: No heartbeat recibido nunca
```

### Probar flujo completo (simulación):

```bash
# Ejecutar flujo híbrido manualmente
docker-compose exec informessi bash scripts/daily-flow-hybrid.sh
```

**Debería:**
1. Verificar PC local
2. Detectar que no está disponible
3. Ejecutar flujo completo
4. Generar mensaje
5. Enviar a Telegram

---

## 🔍 Paso 13: Verificar desde PC Local

### Desde tu PC local, probar conexión:

```bash
# Reemplazar TU_VPS_IP con la IP real
curl http://TU_VPS_IP:8080/status
```

**Debería responder:**
```json
{"status":"ok","registered_pcs":[],"total_pcs":0}
```

**Si no funciona:**
1. Verificar firewall en VPS: `sudo ufw status`
2. Verificar que el servicio esté corriendo: `docker-compose ps`
3. Verificar logs: `docker-compose logs heartbeat-server`

---

## 📊 Paso 14: Monitoreo y Mantenimiento

### Ver logs en tiempo real:

```bash
docker-compose logs -f
```

### Ver uso de recursos:

```bash
docker stats
```

### Reiniciar servicios:

```bash
docker-compose restart
```

### Actualizar código:

```bash
cd /opt/informessi
git pull  # O subir cambios manualmente
docker-compose build
docker-compose up -d
```

---

## 🎉 ¡Listo!

Tu VPS está configurado y listo para:
- ✅ Recibir heartbeats de tu PC local
- ✅ Ejecutar InforMessi cuando PC no esté disponible
- ✅ Generar mensajes con Ollama
- ✅ Enviar a Telegram

**Próximos pasos:**
1. Configurar PC local (ver `docs/setup-hybrido-docker.md`)
2. Probar heartbeat desde PC local
3. Verificar que todo funciona correctamente

---

## 🆘 Problemas Comunes

### No puedo conectar por SSH

- Verificar IP pública
- Verificar que el puerto 22 esté abierto en firewall del proveedor
- Verificar que el servicio SSH esté corriendo: `sudo systemctl status ssh`

### Docker no funciona sin sudo

- Ejecutar: `sudo usermod -aG docker $USER`
- Cerrar sesión y volver a entrar

### Ollama no descarga el modelo

- Verificar espacio en disco: `df -h`
- Verificar logs: `docker-compose logs ollama`
- Intentar de nuevo: `docker-compose exec ollama ollama pull llama3.2`

### Heartbeat server no responde

- Verificar que esté corriendo: `docker-compose ps heartbeat-server`
- Verificar logs: `docker-compose logs heartbeat-server`
- Verificar firewall: `sudo ufw status`

---

*VPS configurado exitosamente* ✅

