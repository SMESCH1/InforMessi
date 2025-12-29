#!/usr/bin/env python3
"""
Sistema RAG de Memoria para evitar repeticiones
Lee informes pasados y extrae información para evitar repetir contenido
MVP - InforMessi
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime, timedelta
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"


def load_past_reports(days_back: int = 30, exclude_date: str = None) -> List[Dict]:
    """Carga informes de los últimos N días"""
    past_reports = []
    
    if not REPORTS_DIR.exists():
        return []
    
    exclude_date_obj = None
    if exclude_date:
        exclude_date_obj = datetime.strptime(exclude_date, "%Y-%m-%d")
    
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    for report_file in sorted(REPORTS_DIR.glob("*.json")):
        try:
            date_str = report_file.stem
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Excluir fecha específica y fechas futuras
            if exclude_date_obj and date_obj.date() == exclude_date_obj.date():
                continue
            if date_obj > datetime.now():
                continue
            if date_obj < cutoff_date:
                continue
            
            with open(report_file, 'r', encoding='utf-8') as f:
                report = json.load(f)
                report['_file_date'] = date_str
                past_reports.append(report)
        except Exception as e:
            continue
    
    return sorted(past_reports, key=lambda x: x.get('_file_date', ''), reverse=True)


def extract_weekly_section_content(report: Dict) -> Dict:
    """Extrae el contenido de la sección semanal de un informe"""
    date_str = report.get('date', report.get('_file_date', ''))
    message = report.get('message', '')
    
    if not date_str or not message:
        return {}
    
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        weekday = date_obj.weekday()  # 0=Lunes, 6=Domingo
    except:
        return {}
    
    section_info = {
        'date': date_str,
        'weekday': weekday,
        'type': None,
        'content': None,
        'players_mentioned': [],
        'topics_mentioned': []
    }
    
    # Determinar tipo de sección según el día
    if weekday in [0, 4]:  # Lunes, Viernes
        section_info['type'] = 'seleccion_mundiales'
    elif weekday in [1, 3]:  # Martes, Jueves
        section_info['type'] = 'jugador_scaloneta'
    elif weekday == 5:  # Sábado
        section_info['type'] = 'dato_mundialista'
    elif weekday == 6:  # Domingo
        section_info['type'] = 'dato_pais_sede'
    else:
        section_info['type'] = 'standard'
    
    # Extraer jugadores mencionados (para jugador_scaloneta)
    if section_info['type'] == 'jugador_scaloneta':
        # Lista de jugadores comunes de la selección
        players = [
            'Messi', 'Di María', 'Martínez', 'Romero', 'De Paul', 'Mac Allister',
            'Álvarez', 'Lautaro', 'Acuña', 'Tagliafico', 'Molina', 'Paredes',
            'Lo Celso', 'Palacios', 'Garnacho', 'Enzo', 'Fernández', 'Scaloni'
        ]
        for player in players:
            if player.lower() in message.lower():
                section_info['players_mentioned'].append(player)
    
    # Extraer temas mencionados
    topics = []
    if 'mundial' in message.lower() or 'mundiales' in message.lower():
        topics.append('mundial')
    if 'selección' in message.lower() or 'argentina' in message.lower():
        topics.append('seleccion')
    if 'escaloneta' in message.lower():
        topics.append('escaloneta')
    
    section_info['topics_mentioned'] = topics
    section_info['content'] = message[:300]  # Primeros 300 caracteres
    
    return section_info


def get_used_weekly_sections(target_date: str, days_back: int = 60) -> Dict:
    """
    Obtiene información sobre secciones semanales ya usadas
    Para evitar repeticiones
    """
    past_reports = load_past_reports(days_back=days_back, exclude_date=target_date)
    
    sections_by_type = defaultdict(list)
    players_used = defaultdict(int)  # Contador de veces que se mencionó cada jugador
    topics_used = defaultdict(int)
    
    for report in past_reports:
        section_info = extract_weekly_section_content(report)
        if not section_info or not section_info['type']:
            continue
        
        section_type = section_info['type']
        sections_by_type[section_type].append(section_info)
        
        # Contar jugadores mencionados
        for player in section_info.get('players_mentioned', []):
            players_used[player] += 1
        
        # Contar temas
        for topic in section_info.get('topics_mentioned', []):
            topics_used[topic] += 1
    
    return {
        'sections_by_type': dict(sections_by_type),
        'players_used': dict(players_used),
        'topics_used': dict(topics_used),
        'total_reports_analyzed': len(past_reports)
    }


def extract_recent_content(reports: List[Dict], max_reports: int = 10) -> Dict:
    """Extrae contenido reciente de informes para evitar repeticiones"""
    recent_content = {
        'recent_dates': [],
        'recent_events': [],
        'recent_news_topics': [],
        'recent_players': [],
        'recent_phrases': []
    }
    
    for report in reports[:max_reports]:
        date = report.get('date', report.get('_file_date', ''))
        if date:
            recent_content['recent_dates'].append(date)
        
        # Extraer eventos mencionados
        data = report.get('data', {})
        events = data.get('events', [])
        for event in events:
            if event.get('description'):
                recent_content['recent_events'].append(event['description'][:100])
        
        # Extraer temas de noticias
        news = data.get('news', [])
        for item in news:
            title = item.get('title', '')
            if title:
                recent_content['recent_news_topics'].append(title[:100])
        
        # Extraer jugadores del mensaje
        message = report.get('message', '')
        players = ['Messi', 'Di María', 'Martínez', 'Romero', 'De Paul', 'Álvarez', 'Lautaro']
        for player in players:
            if player.lower() in message.lower():
                if player not in recent_content['recent_players']:
                    recent_content['recent_players'].append(player)
        
        # Extraer frases características (primeras y últimas líneas)
        if message:
            lines = message.split('\n')
            if lines:
                recent_content['recent_phrases'].append(lines[0][:50])  # Saludo
            if len(lines) > 1:
                recent_content['recent_phrases'].append(lines[-1][:50])  # Cierre
    
    return recent_content


def build_memory_context(target_date: str, days_back: int = 30) -> str:
    """
    Construye el contexto de memoria para evitar repeticiones
    """
    # Obtener información de secciones semanales usadas
    weekly_info = get_used_weekly_sections(target_date, days_back=days_back)
    
    # Obtener informes recientes
    past_reports = load_past_reports(days_back=days_back, exclude_date=target_date)
    recent_content = extract_recent_content(past_reports, max_reports=10)
    
    # Determinar qué sección corresponde al día objetivo
    try:
        date_obj = datetime.strptime(target_date, "%Y-%m-%d")
        weekday = date_obj.weekday()
    except:
        weekday = None
    
    context_parts = []
    
    context_parts.append("### Memoria de Contenido Anterior (Evitar Repeticiones)\n")
    context_parts.append(f"Se analizaron {weekly_info['total_reports_analyzed']} informes anteriores.\n")
    
    # Información específica según el día
    if weekday == 0 or weekday == 4:  # Lunes o Viernes - Selección en Mundiales
        context_parts.append("\n**Sección del día: Selección Argentina en Mundiales**")
        context_parts.append("Evita repetir los mismos temas, momentos históricos o comparaciones que ya se mencionaron en informes anteriores.")
        sections = weekly_info['sections_by_type'].get('seleccion_mundiales', [])
        if sections:
            context_parts.append(f"\nSe han cubierto temas sobre la selección en {len(sections)} ocasiones anteriores.")
            context_parts.append("Varía el enfoque: si antes hablaste de títulos, ahora habla de participaciones; si antes de 1986, ahora de 2022, etc.")
    
    elif weekday == 1 or weekday == 3:  # Martes o Jueves - Jugador
        context_parts.append("\n**Sección del día: Jugador de la Scaloneta**")
        players_used = weekly_info['players_used']
        if players_used:
            context_parts.append("\nJugadores ya destacados recientemente:")
            sorted_players = sorted(players_used.items(), key=lambda x: x[1], reverse=True)
            for player, count in sorted_players[:5]:
                context_parts.append(f"- {player}: {count} vez(es)")
            context_parts.append("\n💡 Prioriza jugadores que NO hayan sido destacados recientemente, o si repites uno, busca un ángulo diferente.")
        else:
            context_parts.append("\nPuedes elegir cualquier jugador de la Scaloneta.")
    
    elif weekday == 5:  # Sábado - Dato Mundialista
        context_parts.append("\n**Sección del día: Dato Mundialista**")
        sections = weekly_info['sections_by_type'].get('dato_mundialista', [])
        if sections:
            context_parts.append(f"\nSe han compartido {len(sections)} datos mundialistas anteriores.")
            context_parts.append("Evita repetir los mismos datos, estadísticas o curiosidades.")
            context_parts.append("Busca nuevos ángulos: formato, sedes, récords, historia, etc.")
    
    elif weekday == 6:  # Domingo - País Sede
        context_parts.append("\n**Sección del día: Dato del País Sede**")
        sections = weekly_info['sections_by_type'].get('dato_pais_sede', [])
        if sections:
            context_parts.append(f"\nSe han compartido {len(sections)} datos sobre países sede anteriores.")
            context_parts.append("Varía entre Estados Unidos, Canadá y México, o busca nuevos aspectos de cada país.")
    
    # Información general sobre contenido reciente
    if recent_content['recent_events']:
        context_parts.append("\n**Eventos recientes mencionados:**")
        context_parts.append("Evita repetir exactamente los mismos eventos si ya se mencionaron.")
    
    if recent_content['recent_news_topics']:
        context_parts.append("\n**Temas de noticias recientes:**")
        unique_topics = list(set(recent_content['recent_news_topics'][:5]))
        for topic in unique_topics:
            context_parts.append(f"- {topic[:80]}...")
        context_parts.append("\n💡 Si mencionas noticias, asegúrate de que sean nuevas o con un enfoque diferente.")
    
    context_parts.append("\n**Instrucciones generales:**")
    context_parts.append("- NO repitas exactamente la misma información, datos o frases de informes anteriores")
    context_parts.append("- Si mencionas algo similar, busca un ángulo o enfoque diferente")
    context_parts.append("- Varía el vocabulario y las expresiones")
    context_parts.append("- Prioriza información nueva o perspectivas frescas")
    
    return "\n".join(context_parts)


def main():
    """Función principal para testing"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sistema de memoria RAG para evitar repeticiones"
    )
    parser.add_argument(
        "--date",
        help="Fecha objetivo (YYYY-MM-DD). Default: hoy",
        default=datetime.now().strftime("%Y-%m-%d")
    )
    parser.add_argument(
        "--days-back",
        type=int,
        default=30,
        help="Días hacia atrás para analizar (default: 30)"
    )
    
    args = parser.parse_args()
    
    print("🧠 Sistema de Memoria RAG")
    print("=" * 50)
    print(f"📅 Fecha objetivo: {args.date}")
    print(f"📊 Analizando últimos {args.days_back} días\n")
    
    # Obtener información de secciones semanales
    weekly_info = get_used_weekly_sections(args.date, days_back=args.days_back)
    print(f"📋 Informes analizados: {weekly_info['total_reports_analyzed']}")
    
    # Mostrar jugadores usados
    if weekly_info['players_used']:
        print("\n👥 Jugadores mencionados recientemente:")
        for player, count in sorted(weekly_info['players_used'].items(), key=lambda x: x[1], reverse=True):
            print(f"   - {player}: {count} vez(es)")
    
    # Mostrar secciones por tipo
    print("\n📑 Secciones por tipo:")
    for section_type, sections in weekly_info['sections_by_type'].items():
        print(f"   - {section_type}: {len(sections)} ocasiones")
    
    # Generar contexto
    print("\n" + "=" * 50)
    print("📝 Contexto de memoria generado:")
    print("=" * 50)
    print(build_memory_context(args.date, days_back=args.days_back))


if __name__ == "__main__":
    main()

