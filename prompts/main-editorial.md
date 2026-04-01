# Generación Diaria - InforMessi

## Datos del Día

- **Fecha**: [FECHA]
- **Cuenta regresiva**: [cuenta regresiva del Mundial 2026]

### Eventos del Día
[Lista de eventos]

### Noticias Relevantes
[Lista de noticias]

---

## Regla de uso de datos

- Si hay eventos: el mensaje DEBE girar alrededor de un evento de la lista, presentándolo como efeméride ("Un día como hoy en [AÑO]...", "Se cumplen X años de...").
- Si hay noticias pero no eventos: basate en al menos 1 noticia.
- Si no hay eventos ni noticias: generá SOLO saludo, cuenta regresiva y cierre. NADA más.
- NUNCA inventes datos, estadísticas, curiosidades, cumpleaños ni información que no esté explícitamente en las listas de arriba. Si un dato no está en las listas, no lo menciones bajo ninguna circunstancia.
- Los eventos históricos incluyen entre corchetes el año original y la antigüedad exacta (ej: "[Año: 1955, hace 71 años]"). Usá EXACTAMENTE esos valores para redactar, pero NUNCA copies los corchetes en el mensaje final. Los corchetes son metadata para vos, NO texto para el lector. Ejemplo: si dice "[Año: 1955, hace 71 años] Argentina campeón de América", escribí "Hace 71 años, Argentina se consagró campeón de América" o "Un día como hoy en 1955, Argentina ganó el título de América". NUNCA escribas "[Año: ...]" en el mensaje.
- Si un evento tiene fecha del AÑO ACTUAL (2026), es un evento del día (partido, amistoso). Presentalo en PRESENTE: "Hoy Argentina enfrenta a...", "Esta noche la Selección debuta en el Mundial a las 22:00...". Incluí horario y estadio.
- Si la cuenta regresiva dice "Día X del Mundial 2026", el torneo está en curso. Adaptá el tono: en vez de "Faltan X días", usá la frase provista.

## Secciones especiales por día

- **Lunes y Viernes**: "Selección Argentina en Mundiales" — SOLO si hay datos provistos sobre el tema
- **Martes y Jueves**: "Jugador de la Scaloneta" — SOLO si hay datos provistos sobre un jugador
- **Sábado**: "Dato Mundialista" — SOLO si hay un dato provisto
- **Domingo**: "Dato del País Sede" — SOLO si hay un dato provisto
- **Miércoles**: Formato estándar

Si no hay datos provistos para la sección especial del día, no la incluyas. No inventes contenido para completarla.

## Estructura

1. Saludo breve (ej: "Buenos días 🇦🇷")
2. Cuenta regresiva (usar la frase exacta provista en "Cuenta regresiva" de los datos del día)
3. Bloque principal — basado en evento o noticia del día, presentado como efeméride. Omitir si no hay datos.
4. Sección especial del día — solo si hay datos provistos para ella.
5. Cierre: "Coronados de gloria vivamos 🩵🤍🩵"

**90-130 palabras. Texto plano. 3-5 emojis. Sin markdown.**

## Ejemplos

Ejemplo 1 (con cumpleaños):
```
Buenos días 🇦🇷

Faltan 247 días para el Mundial 2026 ⚽

🎉 Hoy cumple 37 años Lionel Messi. El capitán de la Scaloneta sigue siendo la referencia mundial del fútbol y prepara su sexta participación en un Mundial 🏆

Coronados de gloria vivamos 🩵🤍🩵
```

Ejemplo 2 (con efeméride de partido):
```
Buenos días 🇦🇷

Faltan 75 días para el Mundial 2026 ⚽

📅 Un día como hoy en 2009, Argentina goleó 4-0 a Venezuela en el debut oficial de Maradona como DT en Eliminatorias. Goles de Messi, Tevez, Maxi Rodríguez y Agüero ⚽

Coronados de gloria vivamos 🩵🤍🩵
```

Ejemplo 3 (con efeméride de título):
```
Buenos días 🇦🇷

Faltan 150 días para el Mundial 2026 ⚽

🏆 Se cumplen 48 años de la obtención del Mundial 1978. El seleccionado albiceleste se coronó campeón del mundo con Mario Alberto Kempes como figura 🇦🇷

Coronados de gloria vivamos 🩵🤍🩵
```

Ejemplo 4 (sin eventos ni noticias):
```
Buenos días 🇦🇷

Faltan 30 días para el Mundial 2026 ⚽

Coronados de gloria vivamos 🩵🤍🩵
```

Ejemplo 5 (durante el Mundial, evento del día):
```
Buenos días 🇦🇷

Día 6 del Mundial 2026 ⚽

🏆 Hoy Argentina debuta en el Mundial enfrentando a Argelia a las 22:00 en el Arrowhead Stadium de Kansas City. La Scaloneta sale a defender el título con Messi al frente 🇦🇷

📅 Un día como hoy en 2006, Messi debutó en mundiales con gol en la goleada 6-0 a Serbia y Montenegro ⚽

Coronados de gloria vivamos 🩵🤍🩵
```

---

Ahora generá el mensaje del día con los datos proporcionados. Usá ÚNICAMENTE la información de las listas de arriba.
