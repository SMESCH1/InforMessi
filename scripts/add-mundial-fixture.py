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
        "description": "Mundial 2026 - Grupo J: Argentina vs Argelia, 22:00 (hora argentina), Arrowhead Stadium, Kansas City."
    },
    {
        "date": "2026-06-22",
        "type": "match",
        "priority": "critical",
        "person": "Selección Argentina",
        "description": "Mundial 2026 - Grupo J: Argentina vs Austria, 14:00 (hora argentina), AT&T Stadium, Dallas."
    },
    {
        "date": "2026-06-27",
        "type": "match",
        "priority": "critical",
        "person": "Selección Argentina",
        "description": "Mundial 2026 - Grupo J: Argentina vs Jordania, 23:00 (hora argentina), AT&T Stadium, Dallas."
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
    # Dieciseisavos de final - Argentina (confirmado 2026-07-03)
    {
        "date": "2026-07-03",
        "type": "match",
        "priority": "critical",
        "person": "Selección Argentina",
        "description": "Mundial 2026 - Dieciseisavos de final: Argentina vs Cabo Verde, 19:00 hora argentina, Hard Rock Stadium, Miami. Árbitro: Drew Fischer (Canadá). El ganador enfrenta en octavos al ganador de Australia vs Egipto."
    },
    # Octavos de final (ventana 4-7 de julio; cruces por definir)
    {
        "date": "2026-07-04",
        "type": "match",
        "priority": "high",
        "person": "N/A",
        "description": "Mundial 2026 - Se juegan los octavos de final. Si Argentina avanza, jugará vs el ganador de Australia/Egipto en el Mercedes-Benz Stadium de Atlanta (día y hora a confirmar)."
    },
    {
        "date": "2026-07-05",
        "type": "match",
        "priority": "high",
        "person": "N/A",
        "description": "Mundial 2026 - Se juegan los octavos de final (ventana 4-7 de julio, cruces por definir)."
    },
    {
        "date": "2026-07-06",
        "type": "match",
        "priority": "high",
        "person": "N/A",
        "description": "Mundial 2026 - Se juegan los octavos de final (ventana 4-7 de julio, cruces por definir)."
    },
    {
        "date": "2026-07-07",
        "type": "match",
        "priority": "high",
        "person": "N/A",
        "description": "Mundial 2026 - Cierran los octavos de final (cruces por definir)."
    },
    # Día de descanso
    {
        "date": "2026-07-08",
        "type": "match",
        "priority": "medium",
        "person": "N/A",
        "description": "Mundial 2026 - Día de descanso antes de los cuartos de final."
    },
    # Cuartos de final (9-11 de julio; cruces a definir)
    {
        "date": "2026-07-09",
        "type": "match",
        "priority": "high",
        "person": "N/A",
        "description": "Mundial 2026 - Se juegan los cuartos de final (9-11 de julio, cruces a definir)."
    },
    {
        "date": "2026-07-10",
        "type": "match",
        "priority": "high",
        "person": "N/A",
        "description": "Mundial 2026 - Se juegan los cuartos de final (9-11 de julio, cruces a definir)."
    },
    {
        "date": "2026-07-11",
        "type": "match",
        "priority": "high",
        "person": "N/A",
        "description": "Mundial 2026 - Cierran los cuartos de final (cruces a definir)."
    },
    # Días previos a semifinales
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
    # Semifinales (sedes confirmadas)
    {
        "date": "2026-07-14",
        "type": "match",
        "priority": "critical",
        "person": "N/A",
        "description": "Mundial 2026 - Semifinal 1, AT&T Stadium, Arlington (Texas). Cruces por definir."
    },
    {
        "date": "2026-07-15",
        "type": "match",
        "priority": "critical",
        "person": "N/A",
        "description": "Mundial 2026 - Semifinal 2, Mercedes-Benz Stadium, Atlanta. Cruces por definir."
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
        "description": "Mundial 2026 - Partido por el tercer puesto, Hard Rock Stadium, Miami."
    },
    # FINAL
    {
        "date": "2026-07-19",
        "type": "match",
        "priority": "critical",
        "person": "N/A",
        "description": "FINAL del Mundial 2026, domingo 19 de julio, MetLife Stadium, Nueva York/Nueva Jersey."
    },
]


def apply_fixture(events_file=EVENTS_FILE, mundial_events=None):
    """Aplica el fixture del Mundial a events.json de forma idempotente.

    Reemplaza por (fecha, tipo): antes de insertar cada evento del fixture,
    elimina los eventos existentes con la misma fecha y el mismo tipo. Así,
    re-correr el script actualiza descripciones/prioridades desactualizadas
    en vez de duplicar o dejar versiones viejas.

    Devuelve (added, replaced, total).
    """
    if mundial_events is None:
        mundial_events = MUNDIAL_EVENTS

    with open(events_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    fixture_keys = {(e["date"], e["type"]) for e in mundial_events}
    existing_keys = {(e.get("date"), e.get("type")) for e in data["events"]}

    kept = []
    replaced = 0
    for existing in data["events"]:
        if (existing.get("date"), existing.get("type")) in fixture_keys:
            replaced += 1
        else:
            kept.append(existing)

    added = sum(
        1 for e in mundial_events if (e["date"], e["type"]) not in existing_keys
    )
    kept.extend(mundial_events)

    # Ordenar por fecha
    kept.sort(key=lambda e: e["date"])
    data["events"] = kept

    with open(events_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return added, replaced, len(kept)


def main():
    added, replaced, total = apply_fixture()
    print(f"Agregados {added} eventos nuevos del Mundial 2026")
    print(f"Reemplazados {replaced} eventos existentes (misma fecha+tipo)")
    print(f"Total eventos: {total}")


if __name__ == "__main__":
    main()
