#!/usr/bin/env python3
"""
Sincroniza informes entre JSON y Markdown
Crea archivos .md más fáciles de editar y los sincroniza con JSON
"""

import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"


def json_to_markdown(report: dict) -> str:
    """Convierte un informe JSON a formato Markdown"""
    date = report.get("date", "N/A")
    status = report.get("status", "draft")
    message = report.get("message", "")
    data = report.get("data", {})
    
    md = f"""# Informe - {date}

**Estado:** {status}  
**Generado:** {report.get('generated_at', 'N/A')}  
**Actualizado:** {report.get('updated_at', 'N/A') or 'N/A'}  
**Publicado:** {report.get('published_at', 'N/A') or 'N/A'}

---

## Datos del Día

- **Días restantes al Mundial:** {data.get('days_remaining', 'N/A')}
- **Eventos:** {len(data.get('events', []))}
- **Noticias:** {len(data.get('news', []))}

---

## Mensaje

{message}

---

## Eventos

"""
    
    events = data.get("events", [])
    if events:
        for event in events:
            event_type = event.get("type", "unknown")
            desc = event.get("description", "Sin descripción")
            priority = event.get("priority", "low")
            md += f"- **[{priority.upper()}]** {event_type}: {desc}\n"
    else:
        md += "No hay eventos del día.\n"
    
    md += "\n---\n\n## Noticias\n\n"
    
    news = data.get("news", [])
    if news:
        for item in news:
            title = item.get("title", "Sin título")
            source = item.get("source", "Sin fuente")
            desc = item.get("description", "")
            md += f"- **{title}** ({source})\n"
            if desc:
                md += f"  {desc[:100]}...\n"
    else:
        md += "No hay noticias del día.\n"
    
    return md


def markdown_to_json(md_file: Path) -> dict:
    """Convierte un archivo Markdown de vuelta a JSON"""
    content = md_file.read_text(encoding='utf-8')
    
    # Extraer fecha del título
    date = md_file.stem  # Nombre del archivo sin extensión
    
    # Extraer mensaje (entre "## Mensaje" y "---")
    msg_start = content.find("## Mensaje")
    msg_end = content.find("---", msg_start + 1)
    
    if msg_start != -1 and msg_end != -1:
        message = content[msg_start:msg_end].replace("## Mensaje", "").strip()
    else:
        message = ""
    
    # Cargar JSON original para mantener datos
    json_file = REPORTS_DIR / f"{date}.json"
    if json_file.exists():
        with open(json_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
    else:
        report = {
            "date": date,
            "generated_at": datetime.now().isoformat(),
            "data": {"events": [], "news": []},
            "status": "draft"
        }
    
    # Actualizar mensaje y status
    report["message"] = message
    if message != report.get("message", ""):
        report["status"] = "updated"
        report["updated_at"] = datetime.now().isoformat()
    
    return report


def sync_to_markdown(date: str = None):
    """Sincroniza JSON a Markdown (crea/actualiza .md)"""
    if date:
        dates = [date]
    else:
        # Sincronizar todos los informes
        dates = [f.stem for f in REPORTS_DIR.glob("*.json")]
    
    for date_str in dates:
        json_file = REPORTS_DIR / f"{date_str}.json"
        md_file = REPORTS_DIR / f"{date_str}.md"
        
        if not json_file.exists():
            continue
        
        with open(json_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        md_content = json_to_markdown(report)
        md_file.write_text(md_content, encoding='utf-8')
        print(f"✅ Sincronizado: {date_str}.md")


def sync_from_markdown(date: str = None):
    """Sincroniza Markdown a JSON (actualiza .json desde .md)"""
    if date:
        dates = [date]
    else:
        # Sincronizar todos los .md
        dates = [f.stem for f in REPORTS_DIR.glob("*.md")]
    
    for date_str in dates:
        md_file = REPORTS_DIR / f"{date_str}.md"
        json_file = REPORTS_DIR / f"{date_str}.json"
        
        if not md_file.exists():
            continue
        
        report = markdown_to_json(md_file)
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Sincronizado: {date_str}.json (status: {report.get('status')})")


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sincroniza informes entre JSON y Markdown"
    )
    parser.add_argument(
        "direction",
        choices=["to-md", "from-md"],
        help="Dirección: to-md (JSON→MD) o from-md (MD→JSON)"
    )
    parser.add_argument(
        "--date",
        help="Fecha específica (YYYY-MM-DD). Default: todas"
    )
    
    args = parser.parse_args()
    
    if args.direction == "to-md":
        sync_to_markdown(args.date)
    else:
        sync_from_markdown(args.date)


if __name__ == "__main__":
    main()

