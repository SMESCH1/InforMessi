# Setup Híbrido con Docker - InforMessi

Guía completa para configurar InforMessi con arquitectura híbrida (PC local + VPS fallback).

## 📋 Arquitectura

```
┌─────────────────┐         ┌─────────────────┐
│   PC Local      │         │   VPS Remoto    │
│                 │         │                 │
│  - Ollama       │         │  - Ollama       │
│  - Scripts      │◄───┐    │  - Scripts      │
│  - Heartbeat    │    │    │  - Heartbeat    │
│    (8:00 AM)    │    │    │    Server       │
│                 │    │    │                 │
└─────────────────┘    │    └─────────────────┘
                       │
                       │ Heartbeat diario
                       │ (antes de 10:15 AM)
                       │
                       ▼
              ┌─────────────────┐
              │  Verificación    │
              │  Disponibilidad│
              │  (8:00 AM)      │
              └─────────────────┘
```

**Flujo:**
1. PC local envía heartbeat UNA VEZ al día (8:00 AM, antes de 10:15 AM)
2. VPS verifica heartbeat del día antes de ejecutar (8:00 AM)
3. Si hay heartbeat del día → PC disponible → VPS no ejecuta
4. Si NO hay heartbeat del día → PC no disponible → VPS ejecuta (fallback)

**Lógica:** Se asume que la PC estará encendida. Solo si no hay señal antes de las 10:15 AM, el VPS ejecuta.

---

## 🖥️ Setup en PC Local

### Paso 1: Instalar Docker y Docker Compose

```bash
# Verificar si Docker está instalado
docker --version
docker-compose --version

# Si no está instalado (Ubuntu/Debian):
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
# Cerrar sesión y volver a entrar
```

### Paso 2: Configurar variables de entorno

Edita `.env` y agrega:

```env
# Heartbeat (agregar estas líneas)
VPS_HEARTBEAT_URL=http://TU_VPS_IP:8080
PC_ID=pc-sebastian

# Telegram (ya deberías tener esto)
TELEGRAM_BOT_TOKEN=tu_token
TELEGRAM_PREVIEW_CHAT_ID=tu_chat_id
TELEGRAM_PUBLISH_CHAT_ID=tu_chat_id_publico

# LLM
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2
```

**⚠️ IMPORTANTE:** Reemplaza `TU_VPS_IP` con la IP pública de tu VPS.

### Paso 3: Construir e iniciar contenedores

```bash
# Construir imágenes
docker-compose build

# Iniciar servicios (sin heartbeat-server en PC local)
docker-compose up -d ollama informessi

# Verificar que están corriendo
docker-compose ps
```

### Paso 4: Descargar modelo de Ollama

```bash
# Entrar al contenedor de Ollama
docker-compose exec ollama ollama pull llama3.2

# Verificar
docker-compose exec ollama ollama list
```

### Paso 5: Configurar heartbeat diario

**Nueva lógica:** El heartbeat se envía UNA VEZ al día, temprano en la mañana (antes de las 10:15 AM).

**Opción 1: Con cron (Recomendado)**

```bash
# Configurar automáticamente
bash scripts/setup-heartbeat-cron.sh

# O manualmente:
crontab -e
# Agregar esta línea (ejecuta a las 8:00 AM):
0 8 * * * cd /ruta/a/InforMessi && python3 scripts/heartbeat.py >> ~/informessi-logs/heartbeat-$(date +\%Y-\%m-\%d).log 2>&1
```

**Opción 2: Al iniciar sesión**

Agregar a `~/.bashrc` o `~/.zshrc`:

```bash
# Enviar heartbeat al iniciar sesión (solo si es antes de las 10:15 AM)
if [ $(date +%H%M) -lt 1015 ]; then
    cd /ruta/a/InforMessi && python3 scripts/heartbeat.py > /dev/null 2>&1 &
fi
```

**Probar manualmente:**

```bash
python3 scripts/heartbeat.py
```

### Paso 6: Configurar cron en PC local

```bash
crontab -e

# Agregar esta línea (ejecuta a las 8:00 AM todos los días)
0 8 * * * cd /home/sebastian-mesch-henriques/Escritorio/Personal/InforMessi && docker-compose exec informessi bash scripts/daily-flow.sh >> ~/informessi-logs/cron-$(date +\%Y-\%m-\%d).log 2>&1
```

**Nota:** Crea el directorio de logs primero:
```bash
mkdir -p ~/informessi-logs
```

---

## ☁️ Setup en VPS

### Paso 1: Elegir y configurar VPS

**Recomendación:** AWS EC2 Free Tier (t2.micro) o Oracle Cloud Free Tier (2 GB RAM)

#### AWS EC2 (Recomendado):
**Ver guía completa:** `docs/guia-configuracion-aws.md`

**Pasos rápidos:**
1. Crear cuenta en AWS
2. **Configurar protección contra cargos (Budgets y alertas)** ⚠️ IMPORTANTE
3. Lanzar instancia EC2 t2.micro (Free tier)
4. Configurar Security Group (puertos 22 y 8080)
5. Conectar por SSH
6. Anotar IP pública

#### Oracle Cloud Free Tier:
1. Crear cuenta en https://cloud.oracle.com
2. Crear instancia "Always Free"
3. Seleccionar Ubuntu 22.04
4. Configurar SSH key
5. Anotar IP pública

### Paso 2: Conectar al VPS

```bash
ssh ubuntu@TU_VPS_IP
# O
ssh root@TU_VPS_IP
```

### Paso 3: Instalar dependencias

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo apt install -y docker-compose

# Agregar usuario a grupo docker
sudo usermod -aG docker $USER
# Cerrar sesión y volver a entrar
```

### Paso 4: Clonar repositorio

```bash
# Instalar Git si no está
sudo apt install -y git

# Clonar repositorio
cd /opt
sudo git clone <TU_REPO_URL> informessi
sudo chown -R $USER:$USER informessi
cd informessi
```

**O si prefieres subir los archivos manualmente:**
```bash
# Crear directorio
sudo mkdir -p /opt/informessi
sudo chown -R $USER:$USER /opt/informessi

# Subir archivos con scp desde tu PC local
scp -r * ubuntu@TU_VPS_IP:/opt/informessi/
```

### Paso 5: Configurar firewall

```bash
# Abrir puertos necesarios
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 8080/tcp  # Heartbeat server
sudo ufw enable
sudo ufw status
```

### Paso 6: Configurar .env en VPS

```bash
cd /opt/informessi
cp .env.example .env
nano .env
```

Agrega:

```env
# Heartbeat
VPS_HEARTBEAT_URL=http://localhost:8080
PC_ID=pc-sebastian
HEARTBEAT_INTERVAL=300

# Telegram (mismo token que en PC local)
TELEGRAM_BOT_TOKEN=tu_token
TELEGRAM_PREVIEW_CHAT_ID=tu_chat_id
TELEGRAM_PUBLISH_CHAT_ID=tu_chat_id_publico

# LLM
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2
```

### Paso 7: Construir e iniciar servicios

```bash
cd /opt/informessi

# Construir imágenes
docker-compose build

# Iniciar todos los servicios (incluyendo heartbeat-server)
docker-compose up -d

# Verificar
docker-compose ps
```

### Paso 8: Descargar modelo de Ollama

```bash
# Entrar al contenedor de Ollama
docker-compose exec ollama ollama pull llama3.2

# Verificar
docker-compose exec ollama ollama list
```

### Paso 9: Configurar cron en VPS

```bash
crontab -e

# Agregar esta línea (verifica antes de ejecutar)
0 8 * * * cd /opt/informessi && docker-compose exec informessi python3 scripts/check-pc-available.py && docker-compose exec informessi bash scripts/daily-flow-hybrid.sh >> ~/informessi-logs/cron-$(date +\%Y-\%m-\%d).log 2>&1
```

**Nota:** Crea el directorio de logs:
```bash
mkdir -p ~/informessi-logs
```

---

## ✅ Verificar Funcionamiento

### En PC Local

```bash
# Ver logs de heartbeat
journalctl --user -u informessi-heartbeat -f

# O si lo ejecutaste manualmente
python3 scripts/heartbeat.py
```

### En VPS

```bash
# Verificar estado del servidor de heartbeat
curl http://localhost:8080/status

# Verificar si PC está disponible
curl http://localhost:8080/check/pc-sebastian

# Ver logs
docker-compose logs -f heartbeat-server
docker-compose logs -f informessi
```

### Probar flujo completo

```bash
# En PC local (cuando esté en horario de trabajo)
docker-compose exec informessi bash scripts/daily-flow.sh

# En VPS (cuando PC no esté disponible)
docker-compose exec informessi bash scripts/daily-flow-hybrid.sh
```

---

## 🔧 Troubleshooting

### Heartbeat no funciona

1. **Verificar que el servidor esté corriendo:**
   ```bash
   docker-compose ps
   ```

2. **Verificar firewall:**
   ```bash
   # En VPS
   sudo ufw status
   # Debe mostrar puerto 8080 abierto
   ```

3. **Verificar URL en .env:**
   ```bash
   # Debe ser IP pública del VPS, no localhost
   VPS_HEARTBEAT_URL=http://TU_VPS_IP:8080
   ```

4. **Probar conexión manualmente:**
   ```bash
   # Desde PC local
   curl http://TU_VPS_IP:8080/status
   ```

### PC no se detecta como disponible

1. **Verificar horario:**
   - Heartbeat solo se envía L-V desde 10 AM
   - Fuera de horario, VPS ejecutará

2. **Verificar logs de heartbeat:**
   ```bash
   # En PC local
   journalctl --user -u informessi-heartbeat -n 50
   ```

3. **Verificar timeout:**
   - Por defecto: 10 minutos
   - Si no hay heartbeat en 10 min, PC se considera offline

### Ollama no funciona

1. **Verificar que el contenedor esté corriendo:**
   ```bash
   docker-compose ps ollama
   ```

2. **Verificar logs:**
   ```bash
   docker-compose logs ollama
   ```

3. **Probar manualmente:**
   ```bash
   docker-compose exec ollama ollama list
   docker-compose exec ollama ollama run llama3.2 "Hola"
   ```

### Scripts no encuentran archivos

1. **Verificar volúmenes en docker-compose.yml:**
   ```yaml
   volumes:
     - ./data:/app/data:ro
     - ./prompts:/app/prompts:ro
   ```

2. **Verificar permisos:**
   ```bash
   ls -la data/ prompts/
   ```

---

## 📊 Monitoreo

### Ver logs en tiempo real

```bash
# Todos los servicios
docker-compose logs -f

# Servicio específico
docker-compose logs -f heartbeat-server
docker-compose logs -f informessi
docker-compose logs -f ollama
```

### Verificar estado de servicios

```bash
docker-compose ps
```

### Verificar uso de recursos

```bash
docker stats
```

---

## 🔄 Actualizar Sistema

### Actualizar código

```bash
# En PC local
cd /home/sebastian-mesch-henriques/Escritorio/Personal/InforMessi
git pull  # O subir cambios manualmente

# Reconstruir contenedores
docker-compose build
docker-compose up -d

# En VPS
cd /opt/informessi
git pull  # O subir cambios manualmente
docker-compose build
docker-compose up -d
```

### Actualizar modelo de Ollama

```bash
docker-compose exec ollama ollama pull llama3.2
```

---

## 📝 Notas Importantes

1. **Horario de trabajo:** El heartbeat solo se envía L-V desde 10 AM. Fuera de ese horario, el VPS ejecutará automáticamente.

2. **IP del VPS:** Debe ser IP pública, accesible desde internet.

3. **Seguridad:** Considera usar autenticación básica en el servidor de heartbeat para producción.

4. **Backups:** Haz backup de `data/events.json` regularmente.

5. **Logs:** Revisa logs periódicamente para detectar problemas.

---

*Sistema híbrido configurado y listo para usar* ✅

