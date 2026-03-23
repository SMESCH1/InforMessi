#!/usr/bin/env python3
"""
Genera contenido para secciones específicas según el día de la semana
Basado en Informesch: lunes/viernes (selección), martes/jueves (jugador), sábado (dato mundialista)
Fase 4 - InforMessi
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def get_weekday_section(weekday: int) -> Dict:
    """
    Retorna la sección específica según el día de la semana
    0=Lunes, 1=Martes, 2=Miércoles, 3=Jueves, 4=Viernes, 5=Sábado, 6=Domingo
    """
    sections = {
        0: {  # Lunes
            "type": "seleccion_mundiales",
            "title": "Selección Argentina en Mundiales",
            "description": "Historia de la selección argentina en los Mundiales",
            "prompt_instruction": "Incluye una sección sobre la historia de la selección argentina en los Mundiales. Puedes mencionar participaciones históricas, títulos, momentos destacados, o comparar con la preparación actual para 2026."
        },
        1: {  # Martes
            "type": "jugador_scaloneta",
            "title": "Jugador de la Scaloneta",
            "description": "Análisis o información sobre un jugador de la selección",
            "prompt_instruction": "Incluye una sección destacando un jugador de la Scaloneta. Puede ser un jugador clave, alguien que esté en buen momento, o información relevante sobre algún integrante del plantel actual."
        },
        2: {  # Miércoles
            "type": "standard",
            "title": None,
            "description": "Formato estándar sin sección especial",
            "prompt_instruction": "Usa el formato estándar del mensaje sin secciones especiales."
        },
        3: {  # Jueves
            "type": "jugador_scaloneta",
            "title": "Jugador de la Scaloneta",
            "description": "Análisis o información sobre un jugador de la selección",
            "prompt_instruction": "Incluye una sección destacando un jugador de la Scaloneta. Puede ser un jugador clave, alguien que esté en buen momento, o información relevante sobre algún integrante del plantel actual."
        },
        4: {  # Viernes
            "type": "seleccion_mundiales",
            "title": "Selección Argentina en Mundiales",
            "description": "Historia de la selección argentina en los Mundiales",
            "prompt_instruction": "Incluye una sección sobre la historia de la selección argentina en los Mundiales. Puedes mencionar participaciones históricas, títulos, momentos destacados, o comparar con la preparación actual para 2026."
        },
        5: {  # Sábado
            "type": "dato_mundialista",
            "title": "Dato Mundialista",
            "description": "Dato curioso o interesante sobre Mundiales",
            "prompt_instruction": "Incluye un dato mundialista destacado. Puede ser sobre la historia de los Mundiales, estadísticas, curiosidades, o información relevante sobre el formato, sedes, o equipos participantes."
        },
        6: {  # Domingo
            "type": "dato_pais_sede",
            "title": "Dato del País Sede",
            "description": "Información sobre Estados Unidos, Canadá o México (países sede 2026)",
            "prompt_instruction": "Incluye un dato sobre los países sede del Mundial 2026 (Estados Unidos, Canadá, México). Puede ser información sobre las ciudades, estadios, cultura futbolera, o curiosidades de estos países relacionados con el Mundial."
        }
    }
    
    return sections.get(weekday, sections[2])  # Default a estándar


def get_player_info(date: str = None) -> Optional[Dict]:
    """Obtiene información de jugadores de la Scaloneta para las secciones"""
    # Lista de jugadores conocidos (puede venir de un archivo JSON)
    players_file = DATA_DIR / "players.json"
    
    available_players = []
    
    if players_file.exists():
        try:
            with open(players_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                available_players = data.get("players", [])
        except:
            pass
    
    # Fallback: lista básica
    if not available_players:
        available_players = [
            {"name": "Lionel Messi", "position": "Delantero", "club": "Inter Miami"},
            {"name": "Ángel Di María", "position": "Delantero", "club": "Benfica"},
            {"name": "Emiliano Martínez", "position": "Arquero", "club": "Aston Villa"},
            {"name": "Cristian Romero", "position": "Defensor", "club": "Tottenham"},
            {"name": "Rodrigo De Paul", "position": "Volante", "club": "Atlético Madrid"},
        ]
    
    # Si hay fecha, usar base de datos persistente para evitar jugadores usados
    if date:
        try:
            from rag_memory_database import MemoryDatabase
            db = MemoryDatabase()
            # Obtener jugadores menos usados de la base de datos
            available_players = db.get_least_used_players(available_players, limit=len(available_players))
        except:
            # Fallback al sistema anterior
            try:
                from rag_memory_system import get_used_weekly_sections
                weekly_info = get_used_weekly_sections(date, days_back=30)
                players_used = weekly_info.get('players_used', {})
                
                # Priorizar jugadores menos usados
                if players_used:
                    # Ordenar por frecuencia de uso (menos usado primero)
                    player_freq = {p['name']: players_used.get(p['name'], 0) for p in available_players}
                    available_players.sort(key=lambda p: player_freq.get(p['name'], 0))
            except:
                pass
    
    # Retornar un jugador (priorizando los menos usados)
    import random
    # Tomar de los primeros 3 menos usados para dar variedad
    return random.choice(available_players[:min(3, len(available_players))])


def get_world_cup_fact(used_facts: list = None) -> str:
    """Retorna un dato mundialista variado no usado recientemente."""
    import random
    facts_file = DATA_DIR / "world-cup-facts.json"
    facts = []
    if facts_file.exists():
        try:
            with open(facts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                facts = data.get("facts", [])
        except Exception:
            pass
    if not facts:
        facts = [
            "El Mundial 2026 será el primero con 48 selecciones.",
            "Argentina es el único equipo que defenderá el título en 2026.",
        ]
    used_facts = used_facts or []
    available = [f for f in facts if f not in used_facts]
    if not available:
        available = facts
    return random.choice(available)


def get_host_country_fact(used_facts: list = None) -> str:
    """Retorna un dato sobre los países sede del Mundial 2026."""
    import random
    facts_file = DATA_DIR / "host-country-facts.json"
    facts = []
    if facts_file.exists():
        try:
            with open(facts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                facts = data.get("facts", [])
        except Exception:
            pass
    if not facts:
        facts = [
            "Estados Unidos: La final se jugará en el estadio MetLife de Nueva York.",
            "México será el primer país en organizar 3 Mundiales: 1970, 1986 y 2026.",
        ]
    used_facts = used_facts or []
    available = [f for f in facts if f not in used_facts]
    if not available:
        available = facts
    return random.choice(available)


def build_weekly_section_prompt(date: str) -> str:
    """Construye el prompt adicional para la sección del día"""
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    weekday = date_obj.weekday()  # 0=Lunes, 6=Domingo

    section = get_weekday_section(weekday)

    if section["type"] == "standard":
        return ""

    prompt = f"\n### Sección Especial del Día ({section['title']})\n\n"
    prompt += f"{section['prompt_instruction']}\n\n"
    
    # Agregar información adicional según el tipo
    if section["type"] == "jugador_scaloneta":
        player = get_player_info(date)  # Pasar fecha para evitar repeticiones
        if player:
            prompt += f"**Jugador del día**: {player.get('name', 'Jugador de la Scaloneta')} "
            prompt += f"({player.get('position', '')}, {player.get('club', '')})\n\n"
            # Usar bio y datos adicionales si están disponibles
            if player.get('bio'):
                prompt += f"**Perfil**: {player.get('bio')}\n\n"
            if player.get('fun_facts'):
                prompt += "**Datos destacados**:\n"
                for fact in player['fun_facts'][:3]:
                    prompt += f"- {fact}\n"
                prompt += "\n"
            if player.get('current_context'):
                prompt += f"**Contexto actual**: {player.get('current_context')}\n\n"
            prompt += "Usa estos datos para escribir la sección. NO inventes datos que no estén aquí.\n"
            prompt += "💡 Si este jugador ya fue destacado recientemente, busca un ángulo diferente basado en los datos disponibles.\n\n"
    
    if section["type"] == "dato_mundialista":
        fact = get_world_cup_fact()
        prompt += f"**Dato sugerido**: {fact}\n"
        prompt += "Usa este dato como base. Puedes expandirlo o agregar contexto, pero no inventes datos adicionales.\n\n"

    if section["type"] == "dato_pais_sede":
        fact = get_host_country_fact()
        prompt += f"**Dato sugerido**: {fact}\n"
        prompt += "Usa este dato como base. Puedes expandirlo con contexto histórico o de fútbol.\n\n"

    prompt += "Esta sección debe integrarse naturalmente en el mensaje, no como un bloque separado.\n"

    return prompt


def main():
    """Función principal para testing"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Genera prompt para sección semanal"
    )
    parser.add_argument(
        "--date",
        help="Fecha en formato YYYY-MM-DD (default: hoy)",
        default=datetime.now().strftime("%Y-%m-%d")
    )
    
    args = parser.parse_args()
    
    date_obj = datetime.strptime(args.date, "%Y-%m-%d")
    weekday = date_obj.weekday()
    weekday_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    section = get_weekday_section(weekday)
    
    print(f"📅 Fecha: {args.date} ({weekday_names[weekday]})")
    print(f"📋 Sección: {section['title'] or 'Estándar'}")
    print(f"📝 Tipo: {section['type']}")
    print()
    print("Prompt adicional:")
    print("=" * 50)
    print(build_weekly_section_prompt(args.date))


if __name__ == "__main__":
    main()

