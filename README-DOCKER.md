# InforMessi - Setup con Docker

Guía rápida para configurar InforMessi con Docker (arquitectura híbrida).

## 🚀 Inicio Rápido

### PC Local

```bash
# 1. Configurar .env
cp .env.example .env
nano .env  # Agregar VPS_HEARTBEAT_URL=http://TU_VPS_IP:8080

# 2. Iniciar servicios
docker-compose up -d ollama informessi

# 3. Descargar modelo
docker-compose exec ollama ollama pull llama3.2

# 4. Configurar heartbeat diario
bash scripts/setup-heartbeat-cron.sh

# 5. Configurar cron
crontab -e
# Agregar: 0 8 * * * cd /ruta/a/InforMessi && docker-compose exec informessi bash scripts/daily-flow.sh
```

### VPS

**Recomendado: AWS EC2 (ver guía completa)**

```bash
# 1. Seguir guía completa: docs/guia-configuracion-aws.md
# 2. IMPORTANTE: Configurar protección contra cargos primero
# 3. Luego ejecutar:
cd /opt/informessi
docker-compose up -d
docker-compose exec ollama ollama pull llama3.2
crontab -e  # Configurar cron
```

**Otras opciones:**
- Oracle Cloud: `docs/guia-configuracion-vps.md`
- Hetzner: `docs/guia-configuracion-vps.md`

## 📚 Documentación Completa

- **Setup completo:** `docs/setup-hybrido-docker.md`
- **Configuración AWS EC2:** `docs/guia-configuracion-aws.md` ⭐ Recomendado
- **Protección contra cargos AWS:** `docs/proteccion-cargos-aws.md` ⚠️ IMPORTANTE
- **Otras opciones VPS:** `docs/guia-configuracion-vps.md`

## 🧪 Probar

```bash
# Probar heartbeat
bash scripts/test-heartbeat.sh

# Probar flujo completo
docker-compose exec informessi bash scripts/daily-flow.sh
```

## 📊 Ver Logs

```bash
docker-compose logs -f
```

---

*Para más detalles, ver la documentación completa en `docs/`*

