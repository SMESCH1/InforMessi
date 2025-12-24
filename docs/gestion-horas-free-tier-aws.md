# Gestión de Horas Free Tier en AWS - InforMessi

Guía completa para optimizar el uso de las 750 horas/mes del free tier de AWS EC2.

## 🎯 Objetivo

Maximizar el uso del free tier (750 horas/mes) apagando la instancia cuando no se necesita.

---

## 📊 Cálculo de Horas

### Free Tier de AWS EC2

- **750 horas/mes** de instancias t2.micro o t3.micro
- **Equivale a:** ~25 horas/día (siempre encendida)
- **O:** ~31 días si se usa solo 24 horas/día

### Estrategia de Ahorro

**Opción 1: Apagado Automático (Recomendado)**
- VPS se enciende solo cuando es necesario
- Se apaga automáticamente después de ejecutar
- **Ahorro:** ~720 horas/mes (si se usa 1 hora/día)

**Opción 2: Horario Específico**
- VPS encendida solo en horarios específicos
- Ejemplo: 8:00-9:00 AM todos los días
- **Ahorro:** ~23 horas/día

---

## 🔄 Sistema de Encendido/Apagado Automático

### Arquitectura

```
┌─────────────────┐
│   PC Local      │
│                 │
│  - Heartbeat    │
│  - Verifica     │
│    disponibilidad│
└────────┬────────┘
         │
         │ Si no hay heartbeat
         ▼
┌─────────────────┐
│  AWS Lambda      │
│  (Opcional)      │
│  - Enciende EC2  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   EC2 Instance  │
│                 │
│  - Ejecuta      │
│    InforMessi   │
│  - Se apaga     │
│    automático   │
└─────────────────┘
```

---

## 🚀 Opción 1: Apagado Automático Después de Ejecutar

### Configuración

1. **Modificar cron en VPS:**

```bash
crontab -e

# Cambiar a usar el script con apagado automático
0 8 * * * cd /opt/informessi && docker-compose exec -T informessi bash scripts/daily-flow-hybrid-with-shutdown.sh >> ~/informessi-logs/cron-$(date +\%Y-\%m-\%d).log 2>&1
```

2. **El script automáticamente:**
   - Verifica si PC local está disponible
   - Si no está disponible, ejecuta InforMessi
   - Si ejecuta exitosamente, apaga la instancia
   - Si falla, deja la instancia encendida para investigar

### Ventajas

- ✅ Ahorra horas automáticamente
- ✅ No requiere intervención manual
- ✅ Se apaga solo después de ejecutar

### Desventajas

- ⚠️ Necesitas encender la instancia manualmente si quieres usarla
- ⚠️ Si falla, la instancia queda encendida

---

## ⏰ Opción 2: Horario Específico con AWS Instance Scheduler

### Configuración

1. **Instalar AWS Instance Scheduler:**

```bash
# Desde AWS Console
# Buscar "AWS Systems Manager" → "Instance Scheduler"
# O usar CloudFormation template
```

2. **Configurar Horario:**

```json
{
  "name": "informessi-schedule",
  "description": "Horario para InforMessi VPS",
  "timezone": "America/Argentina/Buenos_Aires",
  "periods": [
    {
      "name": "morning",
      "beginTime": "08:00",
      "endTime": "09:00",
      "days": ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    }
  ]
}
```

3. **Aplicar a Instancia:**

- Tag la instancia: `Schedule=informessi-schedule`
- La instancia se encenderá/apagará automáticamente

### Ventajas

- ✅ Automático y confiable
- ✅ No requiere scripts adicionales
- ✅ Control total sobre horarios

### Desventajas

- ⚠️ Requiere configuración inicial
- ⚠️ La instancia se enciende incluso si no se necesita

---

## 🔌 Opción 3: Encendido Manual desde PC Local

### Configuración

1. **Instalar AWS CLI en PC local:**

```bash
# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# O con pip
pip install awscli
```

2. **Configurar credenciales:**

```bash
aws configure
# AWS Access Key ID: tu_key
# AWS Secret Access Key: tu_secret
# Default region: us-east-1
# Default output format: json
```

3. **Agregar variables a .env:**

```env
AWS_INSTANCE_ID=i-1234567890abcdef0
AWS_REGION=us-east-1
```

4. **Instalar dependencias:**

```bash
pip install boto3 python-dotenv
```

5. **Usar script para encender:**

```bash
# Desde PC local
python3 scripts/start-instance.sh
```

### Ventajas

- ✅ Control total
- ✅ Solo enciendes cuando lo necesitas
- ✅ Máximo ahorro de horas

### Desventajas

- ⚠️ Requiere intervención manual
- ⚠️ Necesitas encender antes de que se ejecute el cron

---

## 📋 Opción 4: Híbrida (Recomendada)

### Combinación de Opciones

1. **PC Local:**
   - Envía heartbeat a las 8:00 AM
   - Si no está disponible, ejecuta script para encender VPS

2. **VPS:**
   - Se enciende automáticamente (si está apagada)
   - Ejecuta InforMessi
   - Se apaga automáticamente después de ejecutar

### Implementación

**En PC local, modificar heartbeat:**

```python
# scripts/heartbeat-with-vps-start.py
# Si no se puede enviar heartbeat, encender VPS
```

**En VPS, usar script con apagado:**

```bash
# scripts/daily-flow-hybrid-with-shutdown.sh
# Se apaga automáticamente después de ejecutar
```

---

## 📊 Monitoreo de Uso

### Verificar Horas Usadas

1. **AWS Console:**
   - Ve a: https://console.aws.amazon.com/billing/home#/freetier
   - Revisa "EC2 - Compute" → "Hours used"

2. **CloudWatch:**
   - Crea dashboard para monitorear horas de instancia
   - Configura alertas al 80% (600 horas)

### Calcular Uso Estimado

```bash
# Si la instancia está encendida 1 hora/día:
# 1 hora × 30 días = 30 horas/mes
# 750 horas - 30 horas = 720 horas disponibles

# Si está encendida 24 horas/día:
# 24 horas × 30 días = 720 horas/mes
# 750 horas - 720 horas = 30 horas disponibles
```

---

## 🎯 Recomendación Final

### Para Máximo Ahorro:

1. **Usa apagado automático:**
   ```bash
   # En VPS, usar:
   scripts/daily-flow-hybrid-with-shutdown.sh
   ```

2. **Configura timeout:**
   ```env
   MAX_EXECUTION_TIME=15  # minutos
   ```

3. **Monitorea regularmente:**
   - Revisa uso semanalmente
   - Ajusta según necesidad

### Para Máxima Conveniencia:

1. **Usa horario específico:**
   - Instance Scheduler de AWS
   - 8:00-9:00 AM todos los días
   - Ahorra ~23 horas/día

---

## 🔧 Troubleshooting

### La instancia no se apaga

1. **Verificar AWS CLI:**
   ```bash
   aws --version
   ```

2. **Verificar permisos:**
   ```bash
   aws ec2 describe-instances --instance-ids i-xxx
   ```

3. **Verificar IAM Role:**
   - La instancia necesita permisos para detenerse
   - Agregar IAM Role con `ec2:StopInstances`

### La instancia no se enciende

1. **Verificar credenciales AWS:**
   ```bash
   aws configure list
   ```

2. **Verificar Instance ID:**
   ```bash
   # En .env
   AWS_INSTANCE_ID=i-1234567890abcdef0
   ```

3. **Verificar permisos:**
   - Usuario necesita `ec2:StartInstances`

---

## 📝 Checklist de Configuración

- [ ] Script de apagado automático configurado
- [ ] Cron modificado para usar script con apagado
- [ ] AWS CLI instalado en VPS (para apagado)
- [ ] AWS CLI instalado en PC local (para encendido, opcional)
- [ ] IAM Role configurado (permisos para start/stop)
- [ ] Alertas de uso configuradas (80% de horas)
- [ ] Monitoreo semanal configurado

---

## 💡 Consejos Adicionales

1. **Detén la instancia manualmente cuando no la uses:**
   ```bash
   # Desde AWS Console o:
   aws ec2 stop-instances --instance-ids i-xxx
   ```

2. **Usa tags para identificar:**
   - Tag: `Project=InforMessi`
   - Tag: `AutoShutdown=true`

3. **Revisa snapshots:**
   - Elimina snapshots antiguos
   - Solo guarda los necesarios

4. **Monitorea costos:**
   - Revisa Cost Explorer semanalmente
   - Verifica que no haya cargos inesperados

---

*Sistema de gestión de horas optimizado* ✅

