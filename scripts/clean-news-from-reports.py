#!/usr/bin/env python3
"""
Limpia noticias pre-asignadas de todos los reports.
Los eventos (efemérides) se mantienen intactos.
One-time script.
"""

import json
import os
import sys
from pathlib import Path

REPORTS_DIR = Path(__file__).parent.parent / "reports"


def main():
    cleaned = 0
    already_empty = 0
    errors = 0

    for f in sorted(REPORTS_DIR.glob("*.json")):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                report = json.load(fh)

            news = report.get("data", {}).get("news", [])
            if not news:
                already_empty += 1
                continue

            report["data"]["news"] = []
            with open(f, "w", encoding="utf-8") as fh:
                json.dump(report, fh, indent=2, ensure_ascii=False)

            cleaned += 1
            print(f"  Limpiado: {f.name} ({len(news)} noticias removidas)")

        except Exception as e:
            errors += 1
            print(f"  Error en {f.name}: {e}", file=sys.stderr)

    print(f"\nResumen:")
    print(f"  Limpiados: {cleaned}")
    print(f"  Ya vacíos: {already_empty}")
    print(f"  Errores: {errors}")
    print(f"  Total: {cleaned + already_empty + errors}")


if __name__ == "__main__":
    main()
