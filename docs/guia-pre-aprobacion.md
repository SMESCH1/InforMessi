# Guía: Pre-Aprobar Informes

Esta guía explica cómo editar y pre-aprobar informes con anticipación para que se publiquen automáticamente sin pasar por la validación manual.

---

## 🎯 ¿Qué es la Pre-Aprobación?

La pre-aprobación permite marcar un informe como validado antes de que se publique. Los informes pre-aprobados se publican **directamente** en el grupo público sin pasar por el chat de preview.

**Ventajas:**
- ✅ No necesitas revisar día a día
- ✅ Puedes trabajar con anticipación
- ✅ Publicación automática garantizada
- ✅ Menos trabajo manual

---

## 📋 Flujo de Pre-Aprobación

```
1. Generar informes anticipados
   ↓
2. Editar y validar cada uno
   ↓
3. Marcar como pre-aprobado
   ↓
4. El sistema publica automáticamente
```

---

## 🚀 Proceso Paso a Paso

### Paso 1: Generar Informes Anticipados

```bash
# Generar informes para los próximos 15 días
python3 scripts/generate-advance-reports.py --days 15
```

Esto crea informes en `reports/YYYY-MM-DD.json` con estado `draft`.

### Paso 2: Editar y Pre-Aprobar

```bash
# Editar y validar un informe específico
python3 scripts/edit-and-validate-report.py --date 2025-12-31
```

**Opciones disponibles:**

1. **Editar mensaje**
   - Permite modificar el contenido del mensaje
   - Puedes usar un editor externo (nano, vim, code) o editar manualmente
   - Después de editar, pregunta si quieres pre-aprobar

2. **Validar sin editar**
   - Marca el informe como pre-aprobado sin cambios
   - Útil si el mensaje ya está bien

3. **Cancelar**
   - No hace cambios
   - El informe queda sin pre-aprobar

### Paso 3: Verificar Pre-Aprobación

Puedes verificar que un informe esté pre-aprobado:

```bash
# Ver el estado del informe
python3 -c "import json; r=json.load(open('reports/2025-12-31.json')); print(f\"Pre-aprobado: {r.get('pre_approved', False)}\")"
```

O abriendo el archivo JSON y buscando:
```json
{
  "pre_approved": true,
  "pre_approved_at": "2025-12-28T10:30:00"
}
```

---

## ✏️ Editar Mensajes

### Opción 1: Editor Externo (Recomendado)

Cuando seleccionas "Editar mensaje", el script:
1. Crea un archivo temporal con el mensaje actual
2. Abre tu editor por defecto (`$EDITOR` o `nano`)
3. Espera a que guardes y cierres
4. Lee el contenido editado

**Configurar editor:**
```bash
# En tu .bashrc o .zshrc
export EDITOR=nano  # o vim, code, etc.
```

### Opción 2: Edición Manual

Si seleccionas "manual" cuando pregunta el método:
1. Pega el mensaje editado línea por línea
2. Termina con línea vacía + Ctrl+D

### Opción 3: Editar Directamente el JSON

```bash
# Abrir el informe
nano reports/2025-12-31.json

# Editar el campo "message"
{
  "message": "Tu mensaje editado aquí..."
}

# Guardar y luego pre-aprobar
python3 scripts/edit-and-validate-report.py --date 2025-12-31
# Selecciona opción 2: "Validar sin editar"
```

---

## 🔄 Flujo Recomendado

### Trabajo Semanal

**Lunes (o cuando tengas tiempo):**

1. **Generar informes de la semana:**
   ```bash
   python3 scripts/generate-advance-reports.py --days 7
   ```

2. **Revisar y pre-aprobar cada uno:**
   ```bash
   # Día 1
   python3 scripts/edit-and-validate-report.py --date 2025-12-31
   
   # Día 2
   python3 scripts/edit-and-validate-report.py --date 2026-01-01
   
   # ... etc
   ```

3. **Verificar que todos estén pre-aprobados:**
   ```bash
   python3 -c "
   import json
   from pathlib import Path
   from datetime import datetime, timedelta
   
   today = datetime.now()
   for i in range(7):
       date = (today + timedelta(days=i)).strftime('%Y-%m-%d')
       report_file = Path(f'reports/{date}.json')
       if report_file.exists():
           r = json.load(open(report_file))
           status = '✅' if r.get('pre_approved') else '❌'
           print(f'{status} {date}: {r.get(\"pre_approved\", False)}')
   "
   ```

### Trabajo Diario (Si no pre-aprobaste)

Si no pre-aprobaste un informe:
1. GitHub Actions lo envía a preview
2. Recibes mensaje en Telegram
3. Apruebas/rechazas/editas desde Telegram
4. Se publica automáticamente

---

## 📊 Estados de Informes

### Informe Normal (Sin Pre-Aprobar)

```json
{
  "pre_approved": false,
  "status": "updated"
}
```

**Comportamiento:**
- Se envía a preview
- Requiere validación manual
- Se publica después de aprobación o 2 horas

### Informe Pre-Aprobado

```json
{
  "pre_approved": true,
  "pre_approved_at": "2025-12-28T10:30:00",
  "status": "updated"
}
```

**Comportamiento:**
- Se publica directamente
- No pasa por preview
- No requiere validación manual

---

## ⚠️ Notas Importantes

1. **Actualización automática:** Si un informe pre-aprobado se actualiza automáticamente (con noticias nuevas), **mantiene** el estado `pre_approved: true`.

2. **Edición después de pre-aprobar:** Si editas un informe ya pre-aprobado, puedes quitar la pre-aprobación seleccionando "Editar mensaje" y luego no pre-aprobando.

3. **Backup:** Haz backup de los informes antes de editar:
   ```bash
   cp reports/2025-12-31.json reports/2025-12-31.json.backup
   ```

4. **Formato del mensaje:** Asegúrate de que el mensaje editado mantenga:
   - La estructura básica (saludo, contenido, cierre)
   - La frase de cierre: "Coronados de gloria vivamos"
   - Longitud razonable (90-130 palabras)

---

## 🔍 Verificar Pre-Aprobaciones

### Ver todos los informes pre-aprobados

```bash
python3 -c "
import json
from pathlib import Path
from datetime import datetime, timedelta

today = datetime.now()
pre_approved = []
for i in range(30):
    date = (today + timedelta(days=i)).strftime('%Y-%m-%d')
    report_file = Path(f'reports/{date}.json')
    if report_file.exists():
        r = json.load(open(report_file))
        if r.get('pre_approved'):
            pre_approved.append(date)

print(f'Informes pre-aprobados: {len(pre_approved)}')
for date in pre_approved:
    print(f'  ✅ {date}')
"
```

### Ver informes sin pre-aprobar

```bash
python3 -c "
import json
from pathlib import Path
from datetime import datetime, timedelta

today = datetime.now()
not_pre_approved = []
for i in range(30):
    date = (today + timedelta(days=i)).strftime('%Y-%m-%d')
    report_file = Path(f'reports/{date}.json')
    if report_file.exists():
        r = json.load(open(report_file))
        if not r.get('pre_approved'):
            not_pre_approved.append(date)

print(f'Informes sin pre-aprobar: {len(not_pre_approved)}')
for date in not_pre_approved:
    print(f'  ❌ {date}')
"
```

---

## 💡 Tips

1. **Trabaja con anticipación:** Pre-aprueba los informes de la semana el lunes
2. **Revisa el contenido:** Aunque pre-apruebes, revisa que el mensaje esté bien
3. **Agrega contenido:** Antes de pre-aprobar, agrega eventos y media relevantes
4. **Mantén consistencia:** Revisa que los mensajes mantengan el tono editorial

---

## 🐛 Troubleshooting

### El informe no se publica automáticamente

1. Verifica que esté pre-aprobado:
   ```bash
   python3 -c "import json; r=json.load(open('reports/2025-12-31.json')); print(r.get('pre_approved'))"
   ```

2. Verifica que `TELEGRAM_PUBLIC_CHAT_ID` esté configurado

3. Revisa los logs de GitHub Actions

### Quiero quitar la pre-aprobación

Edita el JSON directamente:
```bash
nano reports/2025-12-31.json
# Cambia "pre_approved": true a false
```

O edita el mensaje y no pre-apruebes de nuevo.




