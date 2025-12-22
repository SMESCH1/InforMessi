# Solución: n8n en Docker no puede conectarse al webhook

## Problema

n8n está corriendo en Docker y cuando intenta conectarse a `localhost:8000`, está intentando conectarse al localhost del contenedor, no al localhost de tu máquina.

## Soluciones

Tienes **3 opciones**:

---

## ✅ Opción 1: Usar `host.docker.internal` (Recomendado)

### Paso 1: Reiniciar n8n con acceso al host

```bash
# Detener n8n actual
docker stop n8n
docker rm n8n

# Reiniciar con host.docker.internal
docker run -d \
  --name n8n \
  --restart unless-stopped \
  --add-host=host.docker.internal:host-gateway \
  -p 5678:5678 \
  -v ~/n8n-data:/home/node/.n8n \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=tu_password \
  n8nio/n8n
```

### Paso 2: Actualizar workflow

El workflow ya está actualizado para usar `http://host.docker.internal:8000/execute`.

Si necesitas actualizarlo manualmente:
1. En n8n, edita el nodo "Ejecutar vía HTTP"
2. Cambia la URL a: `http://host.docker.internal:8000/execute`

---

## ✅ Opción 2: Usar IP del Host

### Paso 1: Obtener IP del host

```bash
# Opción A: IP de la interfaz principal
hostname -I | awk '{print $1}'

# Opción B: IP de la red Docker
ip route show default | awk '/default/ {print $3}'
```

### Paso 2: Actualizar workflow

1. En n8n, edita el nodo "Ejecutar vía HTTP"
2. Cambia la URL a: `http://TU_IP:8000/execute`
   - Ejemplo: `http://192.168.1.100:8000/execute`

---

## ✅ Opción 3: Ejecutar webhook en Docker (Más complejo)

Si prefieres tener todo en Docker, puedes ejecutar el webhook también en Docker, pero es más complejo.

---

## 🧪 Probar Conexión

Desde dentro del contenedor de n8n:

```bash
# Entrar al contenedor
docker exec -it n8n sh

# Probar conexión
wget -O- http://host.docker.internal:8000/ || curl http://host.docker.internal:8000/
```

---

## 📋 Checklist

- [ ] n8n reiniciado con `--add-host=host.docker.internal:host-gateway`
- [ ] Servidor webhook corriendo en `localhost:8000`
- [ ] Workflow actualizado con `http://host.docker.internal:8000/execute`
- [ ] Prueba manual exitosa
- [ ] Workflow en n8n funciona

---

**La Opción 1 es la más simple y recomendada** 🚀

