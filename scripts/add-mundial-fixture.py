#!/usr/bin/env python3
"""
One-time script: Agrega el fixture del Mundial 2026 a events.json.
Incluye partidos de Argentina (Grupo J) + inauguración + fases finales.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
EVENTS_FILE = PROJECT_ROOT / "data" / "events.json"

MUNDIAL_EVENTS = [
    # Inauguración
    {
        "date": "2026-06-11",
        "type": "match",
        "priority": "high",
        "person": "N/A",
        "description": "Inauguración del Mundial 2026: México vs Sudáfrica en el Estadio Azteca, Ciudad de México."
    },
    # Fase de grupos - Argentina (Grupo J)
    {
        "date": "2026-06-16",
        "type": "match",
        "priority": "critical",
        "person": "Selección Argentina",
        "description": "Mundial 2026 - Grupo J: Argentina vs Argelia, 21:00 ET, Arrowhead Stadium, Kansas City."
    },
    {
        "date": "2026-06-22",
        "type": "match",
        "priority": "critical",
        "person": "Selección Argentina",
        "description": "Mundial 2026 - Grupo J: Argentina vs Austria, 13:00 ET, AT&T Stadium, Dallas."
    },
    {
        "date": "2026-06-27",
        "type": "match",
        "priority": "critical",
        "person": "Selección Argentina",
        "description": "Mundial 2026 - Grupo J: Argentina vs Jordania, 22:00 ET, AT&T Stadium, Dallas."
    },
    # Fase de grupos - Otros partidos destacados
    {
        "date": "2026-06-12",
        "type": "match",
        "priority": "medium",
        "person": "N/A",
        "description": "Mundial 2026 - Jornada 1 de fase de grupos. Primeros partidos del torneo."
    },
    {
        "date": "2026-06-13",
        "type": "match",
        "priority": "medium",
        "person": "N/A",
        "description": "Mundial 2026 - Continúa la fase de grupos con más debuts."
    },
    {
        "date": "2026-06-14",
        "type": "match",
        "priority": "medium",
        "person": "N/A",
        "description": "Mundial 2026 - Fase de grupos, jornada 1 en pleno desarrollo."
    },
    {
        "date": "2026-06-15",
        "type": "match",
        "priority": "medium",
        "person": "N/A",
        "description": "Mundial 2026 - Fase de grupos, cierran los debuts de jornada 1."
    },
    # Jornada 2 (días entre partidos de Argentina)
    {
        "date": "2026-06-17",
        "type": "match",
        "priority": "medium",
        "person": "N/A",
        "description": "Mundial 2026 - Fase de grupos, jornada 2 en curso."
    },
    {
        "date": "2026-06-18",
        "type": "match",
        "priority": "medium",
        "person": "N/A",
        "description": "Mundial 2026 - Fase de grupos, jornada 2."
    },
    {
        "date": "2026-06-19",
        "type": "match",
        "priority": "medium",
        "person": "N/A",
        "description": "Mundial 2026 - Fase de grupos, jornada 2."
    },
    {
        "date": "2026-06-20",
        "type": "match",
        "priority": "medium",
        "person": "N/A",
        "description": "Mundial 2026 - Fase de grupos, jornada 2."
    },
    {
        "date": "2026-06-21",
        "type": "match",
        "priority": "medium",
        "person": "N/A",
        "description": "Mundial 2026 - Fase de grupos, jornada 2."
    },
    # Jornada 3
    {
        "date": "2026-06-23",
        "type": "match",
        "priority": "medium",
        "person": "N/A",
        "description": "Mundial 2026 - Fase de grupos, jornada 3."
    },
    {
        "date": "2026-06-24",
        "type": "match",
        "priority": "medium",
        "person": "N/A",
        "description": "Mundial 2026 - Fase de grupos, jornada 3."
    },
    {
        "date": "2026-06-25",
        "type": "match",
        "priority": "medium",
        "person": "N/A",
        "description": "Mundial 2026 - Fase de grupos, cierre de jornada 3."
    },
    {
        "date": "2026-06-26",
        "type": "match",
        "priority": "medium",
        "person": "N/A",
        "description": "Mundial 2026 - Últimos partidos de fase de grupos."
    },
    # Treintaidosavos de final (Round of 32)
    {
        "date": "2026-06-28",
        "type": "match",
        "priority": "high",
        "person": "N/A",
        "description": "Mundial 2026 - Comienzan los 32avos de final."
    },
    {
        "date": "2026-06-29",
        "type": "match",
        "priority": "high",
        "person": "N/A",
        "description": "Mundial 2026 - 32avos de final, día 2."
    },
    {
        "date": "2026-06-30",
        "type": "match",
        "priority": "high",
        "person": "N/A",
        "description": "Mundial 2026 - 32avos de final, día 3."
    },
    {
        "date": "2026-07-01",
        "type": "match",
        "priority": "high",
        "person": "N/A",
        "description": "Mundial 2026 - 32avos de final, día 4."
    },
    {
        "date": "2026-07-02",
        "type": "match",
        "priority": "high",
        "person": "N/A",
        "description": "Mundial 2026 - Últimos 32avos de final."
    },
    # Día de descanso
    {
        "date": "2026-07-03",
        "type": "match",
        "priority": "medium",
        "person": "N/A",
        "description": "Mundial 2026 - Día de descanso antes de octavos de final."
    },
    # Octavos de final
    {
        "date": "2026-07-04",
        "type": "match",
        "priority": "high",
        "person": "N/A",
        "description": "Mundial 2026 - Comienzan los octavos de final."
    },
    {
        "date": "2026-07-05",
        "type": "match",
        "priority": "high",
        "person": "N/A",
        "description": "Mundial 2026 - Octavos de final, día 2."
    },
    {
        "date": "2026-07-06",
        "type": "match",
        "priority": "high",
        "person": "N/A",
        "description": "Mundial 2026 - Octavos de final, día 3."
    },
    {
        "date": "2026-07-07",
        "type": "match",
        "priority": "high",
        "person": "N/A",
        "description": "Mundial 2026 - Últimos octavos de final."
    },
    # Días de descanso
    {
        "date": "2026-07-08",
        "type": "match",
        "priority": "medium",
        "person": "N/A",
        "description": "Mundial 2026 - Día de descanso antes de cuartos de final."
    },
    # Cuartos de final
    {
        "date": "2026-07-09",
        "type": "match",
        "priority": "high",
        "person": "N/A",
        "description": "Mundial 2026 - Cuartos de final (2 partidos)."
    },
    {
        "date": "2026-07-10",
        "type": "match",
        "priority": "high",
        "person": "N/A",
        "description": "Mundial 2026 - Cuartos de final (2 partidos)."
    },
    # Descanso
    {
        "date": "2026-07-11",
        "type": "match",
        "priority": "medium",
        "person": "N/A",
        "description": "Mundial 2026 - Día previo a semifinales."
    },
    {
        "date": "2026-07-12",
        "type": "match",
        "priority": "medium",
        "person": "N/A",
        "description": "Mundial 2026 - Día previo a semifinales."
    },
    {
        "date": "2026-07-13",
        "type": "match",
        "priority": "medium",
        "person": "N/A",
        "description": "Mundial 2026 - Día previo a semifinales."
    },
    # Semifinales
    {
        "date": "2026-07-14",
        "type": "match",
        "priority": "critical",
        "person": "N/A",
        "description": "Mundial 2026 - Semifinal 1."
    },
    {
        "date": "2026-07-15",
        "type": "match",
        "priority": "critical",
        "person": "N/A",
        "description": "Mundial 2026 - Semifinal 2."
    },
    # Descanso pre-final
    {
        "date": "2026-07-16",
        "type": "match",
        "priority": "medium",
        "person": "N/A",
        "description": "Mundial 2026 - Previa de la final. Expectativa mundial."
    },
    {
        "date": "2026-07-17",
        "type": "match",
        "priority": "medium",
        "person": "N/A",
        "description": "Mundial 2026 - A dos días de la final."
    },
    # Tercer puesto
    {
        "date": "2026-07-18",
        "type": "match",
        "priority": "high",
        "person": "N/A",
        "description": "Mundial 2026 - Partido por el tercer puesto."
    },
    # FINAL
    {
        "date": "2026-07-19",
        "type": "match",
        "priority": "critical",
        "person": "N/A",
        "description": "FINAL del Mundial 2026, MetLife Stadium, Nueva Jersey."
    },
]


def main():
    with open(EVENTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_dates = {e["date"] for e in data["events"]}
    added = 0

    for event in MUNDIAL_EVENTS:
        # Evitar duplicados por fecha + descripción
        is_dup = any(
            e["date"] == event["date"] and "Mundial 2026" in e.get("description", "")
            for e in data["events"]
        )
        if not is_dup:
            data["events"].append(event)
            added += 1

    # Ordenar por fecha
    data["events"].sort(key=lambda e: e["date"])

    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Agregados {added} eventos del Mundial 2026")
    print(f"Total eventos: {len(data['events'])}")


if __name__ == "__main__":
    main()
