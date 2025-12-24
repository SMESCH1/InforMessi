# Lógica de Heartbeat - InforMessi

## 📋 Concepto

El sistema asume que **la PC local estará encendida por defecto**. Solo si no hay señal antes de las 10:15 AM, el VPS ejecuta como fallback.

## 🔄 Flujo

### PC Local

1. **Al iniciar sesión o temprano en la mañana** (antes de las 10:15 AM):
   - Ejecuta `scripts/heartbeat.py`
   - Envía un heartbeat al VPS indicando que está disponible
   - El heartbeat incluye fecha y hora

2. **El heartbeat se envía UNA VEZ al día**, no continuamente

### VPS

1. **Antes de ejecutar InforMessi** (a las 8:00 AM):
   - Ejecuta `scripts/check-pc-available.py`
   - Verifica si hay un heartbeat del día actual antes de las 10:15 AM
   - Si hay heartbeat → PC está disponible → **NO ejecutar en VPS**
   - Si NO hay heartbeat → PC no está disponible → **Ejecutar en VPS**

## ⏰ Hora Límite

- **10:15 AM**: Hora límite para recibir heartbeat
- Si no hay heartbeat del día antes de las 10:15 AM, el VPS asume que la PC no está disponible

## 📅 Ejemplo de Flujo Diario

### Escenario 1: PC encendida temprano

```
8:00 AM - PC local: Envía heartbeat
8:00 AM - VPS: Verifica heartbeat → Encuentra heartbeat del día → NO ejecuta
8:00 AM - PC local: Ejecuta InforMessi normalmente
```

### Escenario 2: PC no encendida

```
8:00 AM - VPS: Verifica heartbeat → NO encuentra heartbeat del día
8:00 AM - VPS: Ejecuta InforMessi (fallback)
10:15 AM - PC local: Si se enciende después, ya es tarde (VPS ya ejecutó)
```

### Escenario 3: PC encendida después de 10:15 AM

```
8:00 AM - VPS: Verifica heartbeat → NO encuentra heartbeat del día
8:00 AM - VPS: Ejecuta InforMessi (fallback)
10:30 AM - PC local: Se enciende y envía heartbeat (pero ya es tarde)
```

## 🔧 Configuración

### PC Local

**Opción 1: Cron (Recomendado)**

```bash
crontab -e

# Agregar (ejecuta a las 8:00 AM todos los días)
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

### VPS

El VPS ya está configurado para verificar antes de ejecutar (ver `scripts/daily-flow-hybrid.sh`).

## 🧪 Probar

### Desde PC Local

```bash
# Enviar heartbeat manualmente
python3 scripts/heartbeat.py

# Verificar que se recibió en VPS
curl http://TU_VPS_IP:8080/check/pc-sebastian
```

### Desde VPS

```bash
# Verificar disponibilidad de PC
python3 scripts/check-pc-available.py

# Ver estado del servidor
curl http://localhost:8080/status
```

## 📊 Ventajas de esta Lógica

1. **Simplicidad**: Un solo heartbeat al día
2. **Eficiencia**: No hay loop continuo
3. **Claridad**: Lógica simple de entender
4. **Confiabilidad**: VPS siempre tiene una respuesta clara

---

*Lógica de heartbeat simplificada y optimizada* ✅

