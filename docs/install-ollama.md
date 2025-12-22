# Guía de Instalación de Ollama - InforMessi

Esta guía explica cómo instalar Ollama para usar con InforMessi.

## Método 1: Instalación con Script Oficial (Recomendado)

### Linux

```bash
# Ejecutar el script de instalación oficial
curl -fsSL https://ollama.ai/install.sh | sh
```

**Nota**: Este comando requiere permisos de administrador (sudo). Te pedirá tu contraseña.

### Verificar Instalación

```bash
# Verificar que Ollama esté instalado
ollama --version

# Verificar que el servicio esté corriendo
ollama serve
```

## Método 2: Instalación Manual (Sin sudo)

Si no tienes permisos de administrador, puedes instalar Ollama en tu directorio local:

```bash
# Crear directorio local
mkdir -p ~/.local/bin

# Descargar Ollama (ajusta la versión según la última release)
curl -L https://github.com/ollama/ollama/releases/download/v0.1.0/ollama-linux-amd64 -o ~/.local/bin/ollama

# Dar permisos de ejecución
chmod +x ~/.local/bin/ollama

# Agregar al PATH (agregar a ~/.bashrc o ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"

# Verificar
~/.local/bin/ollama --version
```

## Método 3: Usando Docker

```bash
# Ejecutar Ollama en un contenedor Docker
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# Usar desde el host
export OLLAMA_HOST=http://localhost:11434
```

## Después de Instalar

### 1. Iniciar el Servicio

```bash
# Iniciar Ollama en segundo plano
ollama serve
```

O en una terminal separada:

```bash
# Terminal 1: Servicio
ollama serve

# Terminal 2: Comandos
ollama list
```

### 2. Instalar un Modelo

```bash
# Instalar llama3.2 (recomendado para InforMessi)
ollama pull llama3.2

# O instalar otros modelos
ollama pull llama3.1
ollama pull mistral
```

### 3. Verificar que Funciona

```bash
# Listar modelos instalados
ollama list

# Probar el modelo
ollama run llama3.2 "Hola, ¿cómo estás?"
```

### 4. Probar con InforMessi

```bash
# Desde el directorio del proyecto
cd /home/sebastian-mesch-henriques/Escritorio/Personal/InforMessi

# Generar un mensaje
python3 scripts/generate-message.py
```

## Configuración para InforMessi

### Variables de Entorno (Opcional)

Puedes configurar variables de entorno en `.env`:

```env
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
LLM_BASE_URL=http://localhost:11434
```

### Verificar Conexión

```bash
# Verificar que Ollama responda
curl http://localhost:11434/api/tags
```

## Troubleshooting

### Error: "ollama: command not found"

- Verifica que Ollama esté en tu PATH
- Agrega `~/.local/bin` a tu PATH si instalaste localmente
- Reinicia tu terminal después de agregar al PATH

### Error: "Connection refused"

- Verifica que `ollama serve` esté corriendo
- Verifica que el puerto 11434 esté disponible
- Prueba: `curl http://localhost:11434/api/tags`

### Error: "Model not found"

- Instala el modelo: `ollama pull llama3.2`
- Verifica modelos instalados: `ollama list`

### Ollama no inicia

- Verifica permisos: `chmod +x ~/.local/bin/ollama`
- Verifica que no haya otro proceso usando el puerto 11434
- Revisa logs: `ollama serve` mostrará errores en la terminal

## Recursos

- [Documentación oficial de Ollama](https://ollama.ai/docs)
- [Modelos disponibles](https://ollama.ai/library)
- [GitHub de Ollama](https://github.com/ollama/ollama)

---

*Una vez instalado Ollama, podrás usar `scripts/generate-message.py` para generar mensajes reales*


