# Protección contra Cargos en AWS - InforMessi

Guía completa para asegurarte de que NO se generen cargos si se supera el free tier.

## 🎯 Objetivo

Configurar múltiples capas de protección para evitar cargos inesperados en AWS.

---

## 🛡️ Capa 1: AWS Budgets (Recomendado - Primera Línea de Defensa)

### Configurar Budget de $0.01

1. **Ir a AWS Budgets:**
   - Consola AWS → Buscar "Budgets"
   - O directamente: https://console.aws.amazon.com/billing/home#/budgets

2. **Crear Budget:**
   - Haz clic en "Create budget"
   - Tipo: **Cost budget**
   - Nombre: `InforMessi-Protection`
   - Período: **Monthly**
   - Presupuesto: **$0.01** (1 centavo)
   - Filtros: Ninguno (monitorea todo)

3. **Configurar Alertas:**
   - Alerta 1: 80% del presupuesto ($0.008)
   - Alerta 2: 100% del presupuesto ($0.01)
   - Email: Tu email
   - Guarda

**Resultado:** Recibirás email inmediatamente si hay cualquier cargo.

---

## 🚨 Capa 2: CloudWatch Billing Alarms

### Configurar Alarma de Facturación

1. **Ir a CloudWatch:**
   - Consola AWS → Buscar "CloudWatch"
   - O directamente: https://console.aws.amazon.com/cloudwatch/

2. **Crear Alarma:**
   - Alarms → Create alarm
   - Metric: Buscar "EstimatedCharges"
   - Seleccionar: "EstimatedCharges"
   - Statistic: Maximum
   - Period: 6 hours
   - Threshold: **Greater than $0.01**

3. **Configurar Acción:**
   - Notification: Crear nuevo SNS topic
   - Email: Tu email
   - Confirmar suscripción al email
   - Crear alarma

**Resultado:** Alerta automática si la facturación estimada supera $0.01.

---

## 📊 Capa 3: Monitoreo de Free Tier

### Configurar Alertas de Uso de Free Tier

1. **Revisar Límites:**
   - Ve a: https://console.aws.amazon.com/billing/home#/freetier
   - Anota los límites:
     - **EC2:** 750 horas/mes de t2.micro
     - **EBS:** 30 GB de almacenamiento
     - **Data Transfer:** 15 GB saliente/mes

2. **Crear Alarmas de Uso:**
   - En CloudWatch, crea alarmas para:
     - **EC2 Instance Hours:** Alerta al 80% (600 horas)
     - **EBS Storage:** Alerta al 80% (24 GB)
     - **Data Transfer:** Alerta al 80% (12 GB)

---

## 🔒 Capa 4: Service Control Policies (Opcional)

Si tienes una organización AWS, puedes usar SCP para limitar servicios:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": [
        "ec2:RunInstances"
      ],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "ec2:InstanceType": "t2.micro"
        }
      }
    }
  ]
}
```

Esto previene crear instancias que no sean t2.micro.

---

## 📧 Capa 5: Reportes de Facturación

### Configurar Reportes Diarios

1. **Ir a Billing Preferences:**
   - Ve a: https://console.aws.amazon.com/billing/home#/preferences
   - Activa "Receive PDF Invoice By Email"
   - Activa "Receive Billing Alerts"
   - Guarda

2. **Configurar Cost and Usage Reports:**
   - Ve a: https://console.aws.amazon.com/billing/home#/reports
   - Crea reporte diario
   - Formato: CSV
   - Entrega: Email diario

---

## 🔍 Capa 6: Monitoreo Regular

### Checklist Semanal

1. **Revisar Cost Explorer:**
   - Ve a: https://console.aws.amazon.com/cost-management/home
   - Revisa costos de la semana
   - Verifica que no haya servicios inesperados

2. **Revisar Free Tier Usage:**
   - Ve a: https://console.aws.amazon.com/billing/home#/freetier
   - Verifica uso de EC2, EBS, Data Transfer
   - Asegúrate de estar dentro de los límites

3. **Revisar Recursos Activos:**
   - EC2: Verifica que solo tengas 1 instancia t2.micro
   - EBS: Verifica que solo tengas 1 volumen de 20 GB
   - Elimina snapshots, AMIs, o recursos no usados

---

## ⚠️ Qué Hacer si Recibes una Alerta

### Si recibes alerta de $0.01:

1. **Inmediatamente:**
   - Ve a Cost Explorer
   - Identifica qué servicio generó el cargo
   - Revisa los últimos 24 horas

2. **Acciones:**
   - Si es EC2: Verifica que sea t2.micro
   - Si es EBS: Verifica que no tengas volúmenes extra
   - Si es Data Transfer: Revisa tráfico de red
   - Si es otro servicio: Elimínalo inmediatamente

3. **Prevenir:**
   - Detén la instancia si no la necesitas
   - Elimina recursos no usados
   - Revisa Security Groups (pueden generar cargos)

---

## 🎯 Mejores Prácticas

### 1. Usa Solo Recursos de Free Tier

- **EC2:** Solo t2.micro (no t3.micro, no otros tipos)
- **EBS:** Máximo 30 GB total
- **Región:** Usa la misma región para todo (evita cargos de transferencia)

### 2. Detén la Instancia Cuando No la Uses

```bash
# Detener instancia desde AWS Console
# O usar AWS CLI:
aws ec2 stop-instances --instance-ids i-1234567890abcdef0
```

**Ahorra horas de free tier.**

### 3. Configura Auto-Stop (Opcional)

Puedes configurar que la instancia se detenga automáticamente:
- Usando AWS Instance Scheduler
- O con un script que verifique uso y detenga si no hay actividad

### 4. Elimina Recursos No Usados

Regularmente elimina:
- Snapshots de EBS
- AMIs no usadas
- Security Groups no usados
- Key Pairs no usados

### 5. Monitorea Regularmente

- Revisa Cost Explorer semanalmente
- Revisa Free Tier Usage semanalmente
- Revisa emails de alertas inmediatamente

---

## 📋 Checklist de Configuración

Antes de usar AWS, asegúrate de tener:

- [ ] Budget configurado ($0.01)
- [ ] Alertas de Budget configuradas (80% y 100%)
- [ ] CloudWatch Billing Alarm configurado
- [ ] Alertas de Free Tier configuradas
- [ ] Reportes de facturación activados
- [ ] Email de alertas verificado
- [ ] Cost Explorer revisado
- [ ] Solo instancia t2.micro creada
- [ ] Solo 1 volumen EBS de 20 GB
- [ ] Security Groups configurados correctamente

---

## 🆘 Si Ya Se Generó un Cargo

1. **No entres en pánico:** AWS free tier tiene 12 meses
2. **Revisa Cost Explorer:** Identifica el servicio
3. **Elimina el recurso:** Si no lo necesitas
4. **Contacta soporte:** AWS puede hacer ajustes en algunos casos
5. **Aprende:** Evita que vuelva a pasar

---

## 💡 Consejos Adicionales

1. **Usa Tags:** Etiqueta tus recursos para identificar fácilmente
2. **Revisa Security Groups:** Puertos abiertos pueden generar tráfico
3. **Usa la misma región:** Evita cargos de transferencia entre regiones
4. **Configura límites de IAM:** Limita permisos para evitar uso accidental
5. **Documenta todo:** Guarda notas de configuración

---

*Protección completa configurada* ✅

**Recuerda:** La mejor protección es el monitoreo regular y la eliminación de recursos no usados.

