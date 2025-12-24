# Guía Paso a Paso: Configuración de AWS EC2 para InforMessi

Guía detallada para configurar InforMessi en AWS EC2 con protección contra cargos no deseados.

## 🎯 Objetivo

Configurar una instancia EC2 en AWS que:
- Ejecute InforMessi cuando la PC local no esté disponible
- Reciba heartbeats de la PC local
- Tenga Ollama corriendo para generar mensajes
- **NO genere cargos si se supera el free tier**

---

## 📦 Paso 1: Crear Cuenta en AWS

1. **Registrarse:**
   - Ve a https://aws.amazon.com/es/free/
   - Haz clic en "Crear una cuenta gratuita"
   - Completa el registro (requiere tarjeta de crédito, pero no se cobra si usas solo free tier)
   - Verifica email y teléfono

2. **Verificar cuenta:**
   - Espera a que se active (puede tardar unas horas)
   - Inicia sesión en https://console.aws.amazon.com

---

## 🛡️ Paso 2: Configurar Protección contra Cargos (IMPORTANTE)

**⚠️ HAZ ESTO PRIMERO antes de crear recursos**

### 2.1: Configurar Budget y Alertas

1. **Ir a AWS Budgets:**
   - En la consola, busca "Budgets"
   - O ve directamente: https://console.aws.amazon.com/billing/home#/budgets

2. **Crear Budget:**
   - Haz clic en "Create budget"
   - Selecciona "Cost budget"
   - Nombre: `InforMessi-FreeTier-Protection`
   - Período: Mensual
   - Presupuesto: `$0.01` (1 centavo)
   - **Esto te alertará si hay cualquier cargo**

3. **Configurar Alertas:**
   - Agrega alerta al 80% del presupuesto ($0.008)
   - Agrega alerta al 100% del presupuesto ($0.01)
   - Email: Tu email
   - Guarda

### 2.2: Configurar Billing Alerts

1. **Ir a Billing Preferences:**
   - Ve a: https://console.aws.amazon.com/billing/home#/preferences
   - Activa "Receive Billing Alerts"
   - Guarda

2. **Crear CloudWatch Alarm:**
   - Ve a CloudWatch: https://console.aws.amazon.com/cloudwatch/
   - Alarms → Create alarm
   - Metric: "EstimatedCharges"
   - Threshold: `$0.01`
   - Acción: Enviar email cuando se supere
   - Crear

### 2.3: Configurar Límites de Free Tier

1. **Monitorear Free Tier:**
   - Ve a: https://console.aws.amazon.com/billing/home#/freetier
   - Revisa los límites del free tier
   - **EC2 Free Tier:** 750 horas/mes de t2.micro o t3.micro

2. **Configurar Alertas de Uso:**
   - En CloudWatch, crea alarmas para:
     - EC2 Instance Hours: Alerta al 80% (600 horas)
     - Data Transfer: Alerta al 80% del límite

---

## 🚀 Paso 3: Crear Instancia EC2

### 3.1: Lanzar Instancia

1. **Ir a EC2:**
   - En la consola, busca "EC2"
   - O ve directamente: https://console.aws.amazon.com/ec2/

2. **Lanzar Instancia:**
   - Haz clic en "Launch Instance"

3. **Configurar:**
   - **Name:** `informessi-vps`
   - **AMI:** Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Instance type:** `t2.micro` (Free tier eligible) - **IMPORTANTE: Solo este tipo es gratis**
   - **Key pair:** Crea uno nuevo o usa existente
     - Nombre: `informessi-key`
     - Tipo: RSA
     - Formato: `.pem` (para OpenSSH)
     - **Descarga la clave y guárdala en un lugar seguro**

4. **Network settings:**
   - VPC: Dejar por defecto
   - Subnet: Dejar por defecto
   - Auto-assign Public IP: Enable
   - Security group: Crear nuevo
     - Name: `informessi-sg`
     - Description: `Security group for InforMessi`
     - **Inbound rules:**
       - SSH (22) - Source: My IP (o 0.0.0.0/0 si necesitas acceso desde cualquier lugar)
       - Custom TCP (8080) - Source: 0.0.0.0/0 (para heartbeat server)
     - **Outbound rules:** Dejar por defecto (All traffic)

5. **Configure storage:**
   - **IMPORTANTE:** Solo 30 GB de EBS es gratis
   - Size: `20 GB` (suficiente para InforMessi)
   - Volume type: `gp3` (General Purpose SSD)
   - Delete on termination: ✅ (para evitar cargos si eliminas la instancia)

6. **Review and Launch:**
   - Revisa la configuración
   - Haz clic en "Launch Instance"

### 3.2: Obtener IP Pública

1. **Esperar a que la instancia esté "Running"**
2. **Seleccionar la instancia**
3. **Copiar la "Public IPv4 address"**
   - Ejemplo: `54.123.45.67`
   - **Guarda esta IP, la necesitarás**

---

## 🔐 Paso 4: Conectar a la Instancia

### 4.1: Configurar Permisos de la Clave

```bash
# En tu PC local (Linux/Mac)
chmod 400 informessi-key.pem
```

### 4.2: Conectar por SSH

```bash
# Conectar (reemplazar con tu IP y ruta a la clave)
ssh -i ~/path/to/informessi-key.pem ubuntu@TU_IP_PUBLICA

# Primera vez: Confirmar fingerprint (escribe "yes")
```

**Si usas Windows:**
- Usa PuTTY o WSL
- O usa AWS Systems Manager Session Manager (no requiere SSH)

---

## 🛠️ Paso 5: Configurar Sistema Base

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

## 🐳 Paso 6: Instalar Docker

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

## 🔥 Paso 7: Configurar Firewall

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

## 📥 Paso 8: Subir Código de InforMessi

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
scp -i ~/path/to/informessi-key.pem informessi.tar.gz ubuntu@TU_IP_PUBLICA:/tmp/

# En el VPS, descomprimir
ssh -i ~/path/to/informessi-key.pem ubuntu@TU_IP_PUBLICA
cd /opt
sudo mkdir informessi
sudo chown -R $USER:$USER informessi
cd informessi
tar -xzf /tmp/informessi.tar.gz --strip-components=1
```

---

## ⚙️ Paso 9: Configurar Variables de Entorno

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

## 🚀 Paso 10: Construir e Iniciar Servicios

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

## 📦 Paso 11: Descargar Modelo de Ollama

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

## ✅ Paso 12: Verificar Servicios

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

## ⏰ Paso 13: Configurar Apagado Automático (Ahorro de Horas)

### Instalar AWS CLI en VPS

```bash
# Instalar AWS CLI
sudo apt install -y awscli

# O versión más reciente
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verificar
aws --version
```

### Configurar IAM Role para la Instancia

1. **Crear IAM Role:**
   - Ve a IAM → Roles → Create role
   - Trusted entity: EC2
   - Permissions: Agregar policy `AmazonEC2FullAccess` (o crear policy personalizada con solo `ec2:StopInstances`)
   - Name: `InforMessi-EC2-Role`

2. **Asignar Role a Instancia:**
   - EC2 → Instances → Seleccionar instancia
   - Actions → Security → Modify IAM role
   - Seleccionar: `InforMessi-EC2-Role`
   - Save

**O configurar credenciales manualmente:**

```bash
# En VPS
aws configure
# AWS Access Key ID: (dejar vacío si usas IAM Role)
# AWS Secret Access Key: (dejar vacío si usas IAM Role)
# Default region: us-east-1
# Default output format: json
```

### Probar Apagado Automático

```bash
# Probar script de apagado
bash scripts/shutdown-instance.sh
```

**La instancia se apagará automáticamente.**

---

## ⏰ Paso 14: Configurar Cron con Apagado Automático

```bash
# Editar crontab
crontab -e

# Si es primera vez, elegir editor (nano es más fácil)
```

**Agregar esta línea (con apagado automático):**

```cron
# Ejecutar InforMessi diariamente a las 8:00 AM
# Verifica si PC local está disponible antes de ejecutar
# Se apaga automáticamente después de ejecutar exitosamente
0 8 * * * cd /opt/informessi && docker-compose exec -T informessi bash scripts/daily-flow-hybrid-with-shutdown.sh >> ~/informessi-logs/cron-$(date +\%Y-\%m-\%d).log 2>&1
```

**O sin apagado automático (si prefieres control manual):**

```cron
# Ejecutar InforMessi diariamente a las 8:00 AM
# Verifica si PC local está disponible antes de ejecutar
0 8 * * * cd /opt/informessi && docker-compose exec -T informessi python3 scripts/check-pc-available.py > /dev/null 2>&1 || docker-compose exec -T informessi bash scripts/daily-flow-hybrid.sh >> ~/informessi-logs/cron-$(date +\%Y-\%m-\%d).log 2>&1
```

**⚠️ IMPORTANTE:** El script con apagado automático ahorra horas del free tier. La instancia se apagará después de ejecutar exitosamente.

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

## 🧪 Paso 15: Probar Flujo Completo

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

## 🔍 Paso 16: Verificar desde PC Local

### Desde tu PC local, probar conexión:

```bash
# Reemplazar TU_IP_PUBLICA con la IP real de tu instancia EC2
curl http://TU_IP_PUBLICA:8080/status
```

**Debería responder:**
```json
{"status":"ok","registered_pcs":[],"total_pcs":0}
```

**Si no funciona:**
1. Verificar Security Group en AWS (puerto 8080 debe estar abierto)
2. Verificar firewall en VPS: `sudo ufw status`
3. Verificar que el servicio esté corriendo: `docker-compose ps`
4. Verificar logs: `docker-compose logs heartbeat-server`

---

## 💰 Paso 17: Configurar Protección Adicional contra Cargos

### 16.1: Configurar Auto-Stop (Opcional pero Recomendado)

Para ahorrar horas de free tier, puedes configurar que la instancia se detenga automáticamente:

```bash
# Crear script de auto-stop (solo si no hay heartbeat del día)
# Esto se puede hacer con un cron job que verifique y detenga la instancia
# si no hay actividad
```

**O usar AWS Instance Scheduler:**
- Configura para detener la instancia fuera de horarios de uso
- Ahorra horas de free tier

### 16.2: Monitorear Uso Regularmente

1. **Revisar uso de Free Tier:**
   - Ve a: https://console.aws.amazon.com/billing/home#/freetier
   - Revisa semanalmente

2. **Revisar Cost Explorer:**
   - Ve a: https://console.aws.amazon.com/cost-management/home
   - Revisa costos diarios

3. **Configurar Reportes:**
   - En Billing, configura reportes diarios por email

### 16.3: Configurar Límites de Servicio

1. **Service Control Policies (SCP):**
   - Si tienes una organización AWS, puedes usar SCP para limitar servicios

2. **IAM Policies:**
   - Limita permisos de la instancia para evitar uso accidental de servicios de pago

---

## 📊 Paso 18: Monitoreo y Mantenimiento

### Encender Instancia Manualmente (si está apagada)

**Desde AWS Console:**
1. EC2 → Instances
2. Seleccionar instancia
3. Instance state → Start instance

**Desde PC local (si configuraste AWS CLI):**

```bash
# Agregar a .env en PC local:
# AWS_INSTANCE_ID=i-1234567890abcdef0
# AWS_REGION=us-east-1

# Instalar dependencias:
pip install boto3 python-dotenv

# Encender instancia:
python3 scripts/start-instance.sh
```

**Desde línea de comandos (si tienes AWS CLI configurado):**

```bash
aws ec2 start-instances --instance-ids i-1234567890abcdef0 --region us-east-1
```

### Verificar Estado de Instancia

```bash
# Desde VPS (si está encendida)
curl http://169.254.169.254/latest/meta-data/instance-id

# Desde PC local
aws ec2 describe-instances --instance-ids i-xxx --query 'Reservations[0].Instances[0].State.Name'
```

---

## 📊 Paso 19: Monitoreo de Horas Usadas

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

## 🆘 Problemas Comunes

### No puedo conectar por SSH

- Verificar Security Group: puerto 22 debe estar abierto
- Verificar que la instancia esté "Running"
- Verificar permisos de la clave: `chmod 400 informessi-key.pem`
- Verificar IP pública correcta

### Docker no funciona sin sudo

- Ejecutar: `sudo usermod -aG docker $USER`
- Cerrar sesión y volver a entrar

### Ollama no descarga el modelo

- Verificar espacio en disco: `df -h`
- Verificar logs: `docker-compose logs ollama`
- Intentar de nuevo: `docker-compose exec ollama ollama pull llama3.2`

### Heartbeat server no responde

- Verificar Security Group: puerto 8080 debe estar abierto
- Verificar que esté corriendo: `docker-compose ps heartbeat-server`
- Verificar logs: `docker-compose logs heartbeat-server`
- Verificar firewall: `sudo ufw status`

### Recibo alertas de facturación

- **Si recibes alerta de $0.01:**
  - Revisa Cost Explorer inmediatamente
  - Verifica que estés usando solo t2.micro
  - Verifica que no tengas otros recursos corriendo
  - Detén la instancia si no la necesitas

---

## 💡 Consejos para Mantener Free Tier

1. **Usa solo t2.micro:** No uses otros tipos de instancia
2. **Detén la instancia cuando no la uses:** Ahorra horas de free tier
3. **Monitorea regularmente:** Revisa uso semanalmente
4. **Configura alertas:** Te avisarán antes de que se generen cargos
5. **Elimina recursos no usados:** Snapshots, AMIs, etc.

---

## 🎉 ¡Listo!

Tu instancia EC2 está configurada y protegida contra cargos no deseados.

**Próximos pasos:**
1. Configurar PC local (ver `docs/setup-hybrido-docker.md`)
2. Probar heartbeat desde PC local
3. Verificar que todo funciona correctamente

---

*Instancia AWS EC2 configurada exitosamente con protección contra cargos* ✅

