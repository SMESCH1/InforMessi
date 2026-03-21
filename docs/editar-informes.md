# Cómo Editar Informes - Guía Completa

Guía para visualizar y editar informes de forma amigable.

## 🎯 Opciones Disponibles

### Opción 1: Visualizar Informe (Solo Lectura)

Muestra el informe de forma legible en la terminal:

```bash
# Ver informe de hoy
python3 scripts/view-report.py

# Ver informe de una fecha específica
python3 scripts/view-report.py --date 2025-12-28
```

**Salida:**
- Estado del informe
- Datos del día (eventos, noticias)
- Mensaje completo
- Estadísticas (palabras)

---

### Opción 2: Editar con Editor de Texto

Edita el mensaje directamente con tu editor favorito:

```bash
# Editar informe de hoy (auto-detecta editor)
python3 scripts/edit-report.py

# Editar informe específico
python3 scripts/edit-report.py --date 2025-12-28

# Especificar editor
python3 scripts/edit-report.py --date 2025-12-28 --editor nano
python3 scripts/edit-report.py --date 2025-12-28 --editor vim
python3 scripts/edit-report.py --date 2025-12-28 --editor code  # VS Code
```

**Características:**
- ✅ Abre el mensaje en tu editor favorito
- ✅ Automáticamente cambia status a `"updated"`
- ✅ Guarda timestamp de actualización
- ✅ Valida cambios antes de guardar

---

### Opción 3: Editar en Markdown (Recomendado) ⭐

Crea archivos `.md` más fáciles de editar y sincroniza con JSON:

#### Paso 1: Generar archivos Markdown

```bash
# Generar .md para todos los informes
python3 scripts/sync-reports-md.py to-md

# Generar .md para una fecha específica
python3 scripts/sync-reports-md.py to-md --date 2025-12-28
```

Esto crea `reports/2025-12-28.md` con el contenido formateado.

#### Paso 2: Editar el archivo Markdown

```bash
# Editar con tu editor favorito
nano reports/2025-12-28.md
# o
code reports/2025-12-28.md
# o cualquier editor
```

El archivo Markdown tiene esta estructura:

```markdown
# Informe - 2025-12-28

**Estado:** draft
**Generado:** 2025-12-28T18:46:55
...

## Mensaje

Buenos días 🇦🇷

Faltan 165 días para el Mundial 2026.
...

## Eventos
- [HIGH] birthday: Cumpleaños de...
...

## Noticias
- Noticia 1 (TyC Sports)
...
```

#### Paso 3: Sincronizar de vuelta a JSON

```bash
# Sincronizar todos los .md a JSON
python3 scripts/sync-reports-md.py from-md

# Sincronizar uno específico
python3 scripts/sync-reports-md.py from-md --date 2025-12-28
```

**Automáticamente:**
- ✅ Actualiza el mensaje en el JSON
- ✅ Cambia status a `"updated"`
- ✅ Guarda timestamp de actualización

---

## 📋 Flujo de Trabajo Recomendado

### Para Editar un Informe:

1. **Generar Markdown:**
   ```bash
   python3 scripts/sync-reports-md.py to-md --date 2025-12-28
   ```

2. **Editar el archivo:**
   ```bash
   code reports/2025-12-28.md
   # Edita la sección "## Mensaje"
   ```

3. **Sincronizar de vuelta:**
   ```bash
   python3 scripts/sync-reports-md.py from-md --date 2025-12-28
   ```

4. **Verificar:**
   ```bash
   python3 scripts/view-report.py --date 2025-12-28
   ```

---

## 🎨 Ventajas de Cada Método

### `view-report.py`
- ✅ Rápido para ver contenido
- ✅ Formato legible en terminal
- ❌ Solo lectura

### `edit-report.py`
- ✅ Edición directa
- ✅ Cambio automático de status
- ⚠️ Requiere editor en terminal

### `sync-reports-md.py` (Recomendado)
- ✅ Archivos Markdown fáciles de editar
- ✅ Puedes usar cualquier editor
- ✅ Formato más legible
- ✅ Sincronización bidireccional
- ✅ Cambio automático de status

---

## 💡 Tips

1. **Usa Markdown para ediciones frecuentes:**
   - Más fácil de leer y editar
   - Puedes usar cualquier editor
   - Mejor para versionar en Git

2. **Mantén sincronizados:**
   - Si editas JSON directamente, regenera MD
   - Si editas MD, sincroniza a JSON antes de generar nuevos informes

3. **Editor favorito:**
   - VS Code: `code reports/2025-12-28.md`
   - Nano: `nano reports/2025-12-28.md`
   - Vim: `vim reports/2025-12-28.md`

---

## 🔄 Automatización (Opcional)

Puedes crear un alias en tu `.bashrc` o `.zshrc`:

```bash
# Agregar a ~/.bashrc o ~/.zshrc
alias edit-informe='python3 /ruta/a/InforMessi/scripts/edit-report.py'
alias ver-informe='python3 /ruta/a/InforMessi/scripts/view-report.py'
alias sync-md='python3 /ruta/a/InforMessi/scripts/sync-reports-md.py'
```

Luego usar:
```bash
edit-informe --date 2025-12-28
ver-informe --date 2025-12-28
```

---

*Última actualización: 2025-12-28*

