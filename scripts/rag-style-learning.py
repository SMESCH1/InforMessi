#!/usr/bin/env python3
"""
Sistema RAG para aprendizaje de estilo desde informes editados
Extrae ejemplos de estilo de informes con status "updated" o "published"
"""

import json
import os
from pathlib import Path
from typing import List, Dict
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"


def load_edited_reports(min_examples: int = 3, max_examples: int = 10) -> List[Dict]:
    """
    Carga informes que han sido editados (updated o published)
    Estos representan el estilo del usuario
    """
    edited_reports = []
    
    if not REPORTS_DIR.exists():
        return []
    
    # Buscar todos los informes
    for report_file in sorted(REPORTS_DIR.glob("*.json"), reverse=True):
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            # Solo incluir informes editados o publicados
            status = report.get("status", "draft")
            if status in ["updated", "published"]:
                edited_reports.append(report)
                
                if len(edited_reports) >= max_examples:
                    break
        except Exception as e:
            print(f"⚠️  Error al cargar {report_file}: {e}")
            continue
    
    # Si no hay suficientes, incluir algunos draft recientes
    if len(edited_reports) < min_examples:
        for report_file in sorted(REPORTS_DIR.glob("*.json"), reverse=True):
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                
                if report.get("status") == "draft" and report not in edited_reports:
                    edited_reports.append(report)
                    
                    if len(edited_reports) >= min_examples:
                        break
            except:
                continue
    
    return edited_reports


def extract_style_examples(reports: List[Dict]) -> str:
    """
    Extrae ejemplos de estilo de los informes editados
    Formatea para incluir en el prompt del LLM
    """
    if not reports:
        return ""
    
    examples = []
    examples.append("### Ejemplos de Estilo (de informes editados anteriormente):\n")
    
    for i, report in enumerate(reports[:5], 1):  # Máximo 5 ejemplos
        date = report.get("date", "N/A")
        message = report.get("message", "")
        
        # Extraer solo las partes más relevantes del mensaje
        lines = message.split('\n')
        # Tomar primeras líneas y últimas líneas (saludo y cierre)
        relevant_lines = lines[:3] + lines[-3:] if len(lines) > 6 else lines
        
        examples.append(f"**Ejemplo {i} - {date}:**")
        examples.append("\n".join(relevant_lines))
        examples.append("")  # Línea en blanco
    
    return "\n".join(examples)


def get_style_context() -> str:
    """
    Obtiene contexto de estilo desde informes editados
    Para usar en el prompt de generación
    """
    edited_reports = load_edited_reports(min_examples=3, max_examples=5)
    
    if not edited_reports:
        return ""
    
    style_examples = extract_style_examples(edited_reports)
    
    context = f"""
---

## Contexto de Estilo Aprendido

Basado en {len(edited_reports)} informes editados anteriormente, sigue estos patrones de estilo:

{style_examples}

**Instrucciones:**
- Mantén el tono y estructura similar a los ejemplos anteriores
- Usa frases y expresiones similares cuando sea apropiado
- Conserva el estilo argentino, cercano y editorial
- Respeta la longitud objetivo (90-130 palabras)
"""
    
    return context


def main():
    """Función principal - para testing"""
    print("📚 RAG - Aprendizaje de Estilo")
    print("=" * 50)
    
    edited_reports = load_edited_reports()
    print(f"\n📊 Informes editados encontrados: {len(edited_reports)}")
    
    if edited_reports:
        print("\n📅 Fechas de informes editados:")
        for report in edited_reports:
            date = report.get("date", "N/A")
            status = report.get("status", "draft")
            updated = report.get("updated_at", "N/A")
            print(f"   - {date} ({status}) - Actualizado: {updated}")
        
        print("\n📝 Contexto de estilo generado:")
        print(get_style_context())
    else:
        print("\n⚠️  No se encontraron informes editados")
        print("   Edita algunos informes en reports/ para que el sistema aprenda tu estilo")


if __name__ == "__main__":
    main()

