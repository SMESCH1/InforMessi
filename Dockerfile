# Dockerfile para InforMessi
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt flask

# Copiar código del proyecto
COPY . .

# Crear directorio para datos temporales
RUN mkdir -p /tmp/informessi

# Script de entrada por defecto
CMD ["python3", "--version"]

