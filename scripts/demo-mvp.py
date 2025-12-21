#!/usr/bin/env python3
"""
Script de demostración del MVP - Muestra cómo se construye el prompt
Útil cuando Ollama no está disponible
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Configuración
PROJECT_ROOT = Path(__file__).parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
DATA_DIR = PROJECT_ROOT / "data"

def load_prompt(filename):
    """Carga un archivo de prompt desde prompts/"""
    filepath = PROMPTS_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Prompt no encontrado: {filename}")
    return filepath.read_text(encoding='utf-8')

def load_mock_data(filename="mock-data.json"):
    """Carga datos mock desde data/"""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Datos mock no encontrados: {filename}")
    return json.loads(filepath.read_text(encoding='utf-8'))

def calculate_days_remaining(mundial_date, current_date):
    """Calcula días restantes hasta el Mundial"""
    mundial = datetime.strptime(mundial_date, "%Y-%m-%d").date()
    current = datetime.strptime(current_date, "%Y-%m-%d").date()
    return (mundial - current).days

def build_prompt(data):
    """Construye el prompt completo con system prompt y datos del día"""
    
    # Cargar prompts
    system_prompt = load_prompt("system-prompt.md")
    main_prompt = load_prompt("main-editorial.md")
    
    # Calcular días restantes
    days_remaining = calculate_days_remaining(
        data["mundial_2026_start"],
        data["date"]
    )
    
    # Formatear eventos
    events_text = "No hay eventos importantes del día."
    if data["events"]:
        events_list = []
        for event in data["events"]:
            if event["type"] == "birthday":
                events_list.append(
                    f"- {event['person']} cumple {event['age']} años ({event['description']})"
                )
            elif event["type"] == "match":
                events_list.append(
                    f"- Partido: Argentina vs {event['opponent']} en {event['venue']} a las {event['time']} ({event['description']})"
                )
            else:
                events_list.append(f"- {event['description']}")
        events_text = "\n".join(events_list)
    
    # Formatear noticias
    news_text = "No hay noticias relevantes del día."
    if data["news"]:
        news_list = []
        for news in data["news"]:
            news_list.append(f"- {news['title']}: {news['summary']}")
        news_text = "\n".join(news_list)
    
    # Construir prompt con datos
    prompt = f"""{system_prompt}

---

{main_prompt}

### Datos del Día
- **Fecha**: {data['date']}
- **Días restantes al Mundial 2026**: {days_remaining} días
- **Clima AMBA**: min {data['weather']['amba']['min']}° / max {data['weather']['amba']['max']}°
- **Clima La Plata**: min {data['weather']['la_plata']['min']}° / max {data['weather']['la_plata']['max']}°
- **Link clima Argentina**: {data['weather']['link_argentina']}

### Eventos del Día
{events_text}

### Noticias Relevantes
{news_text}
"""
    
    return prompt

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Demostración del MVP - Muestra el prompt construido"
    )
    parser.add_argument(
        "--data",
        default="mock-data.json",
        help="Archivo de datos mock a usar (default: mock-data.json)"
    )
    parser.add_argument(
        "--output",
        help="Archivo donde guardar el prompt"
    )
    
    args = parser.parse_args()
    
    print("🚀 InforMessi - Demostración del MVP")
    print("=" * 70)
    print("⚠️  NOTA: Este es un modo demostración (Ollama no requerido)")
    print("=" * 70)
    print()
    
    # Cargar datos
    print(f"📂 Cargando datos mock: {args.data}")
    data = load_mock_data(args.data)
    print(f"   ✅ Fecha: {data['date']}")
    print(f"   ✅ Días restantes: {calculate_days_remaining(data['mundial_2026_start'], data['date'])}")
    print(f"   ✅ Eventos: {len(data['events'])}")
    print(f"   ✅ Noticias: {len(data['news'])}")
    
    # Construir prompt
    print("\n📝 Construyendo prompt completo...")
    prompt = build_prompt(data)
    
    # Mostrar resumen
    print("\n" + "=" * 70)
    print("📋 RESUMEN DEL PROMPT CONSTRUIDO:")
    print("=" * 70)
    print(f"   Longitud total: {len(prompt)} caracteres")
    print(f"   Líneas: {len(prompt.splitlines())}")
    print()
    
    # Mostrar prompt (truncado si es muy largo)
    print("=" * 70)
    print("📄 PROMPT COMPLETO:")
    print("=" * 70)
    
    if len(prompt) > 3000:
        print(prompt[:2000])
        print("\n... [prompt truncado para visualización] ...")
        print("\n" + prompt[-500:])
    else:
        print(prompt)
    
    print("=" * 70)
    
    # Guardar si se especificó output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(prompt, encoding='utf-8')
        print(f"\n💾 Prompt guardado en: {output_path}")
    
    # Información adicional
    print("\n" + "=" * 70)
    print("ℹ️  INFORMACIÓN:")
    print("=" * 70)
    print("   Este prompt sería enviado al LLM (Ollama) para generar el mensaje.")
    print("   Para probar con LLM real, instala Ollama y usa generate-message.py")
    print()
    print("   Instalar Ollama:")
    print("   curl -fsSL https://ollama.ai/install.sh | sh")
    print()
    print("   Luego ejecutar:")
    print(f"   python3 scripts/generate-message.py --data {args.data}")

if __name__ == "__main__":
    main()

