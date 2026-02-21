#!/usr/bin/env python3
"""
Base de datos persistente para rastrear contenido usado
Evita repeticiones a largo plazo
MVP - InforMessi
"""

import json
import unicodedata
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
from collections import defaultdict


def _normalize_text(text: str) -> str:
    """Lowercase, strip accents, collapse whitespace."""
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return " ".join(text.split())

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MEMORY_DB_FILE = DATA_DIR / "memory-database.json"


class MemoryDatabase:
    """Base de datos en memoria para rastrear contenido usado"""
    
    def __init__(self):
        self.db_file = MEMORY_DB_FILE
        self.data = self._load_database()
    
    def _load_database(self) -> Dict:
        """Carga la base de datos desde archivo"""
        if not self.db_file.exists():
            return self._create_empty_database()
        
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Asegurar estructura
                return self._ensure_structure(data)
        except Exception as e:
            print(f"⚠️  Error al cargar base de datos: {e}")
            return self._create_empty_database()
    
    def _create_empty_database(self) -> Dict:
        """Crea una base de datos vacía"""
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "players_used": {},  # {player_name: [dates]}
            "weekly_sections": {
                "seleccion_mundiales": [],  # [dates]
                "jugador_scaloneta": [],  # [dates]
                "dato_mundialista": [],  # [dates]
                "dato_pais_sede": []  # [dates]
            },
            "topics_mentioned": {},  # {topic: [dates]}
            "events_mentioned": {},  # {event_description: [dates]}
            "news_topics": {},  # {news_title: [dates]}
            "facts_used": {},  # {fact_text: [dates]}
            "phrases_used": []  # [{"date": date, "phrase": phrase}]
        }
    
    def _ensure_structure(self, data: Dict) -> Dict:
        """Asegura que la estructura de datos sea correcta"""
        default = self._create_empty_database()
        for key in default:
            if key not in data:
                data[key] = default[key]
        return data
    
    def save(self):
        """Guarda la base de datos en archivo"""
        self.data["last_updated"] = datetime.now().isoformat()
        
        # Crear directorio si no existe
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Error al guardar base de datos: {e}")
    
    def record_player_used(self, player_name: str, date: str):
        """Registra que un jugador fue usado en una fecha"""
        if player_name not in self.data["players_used"]:
            self.data["players_used"][player_name] = []
        
        if date not in self.data["players_used"][player_name]:
            self.data["players_used"][player_name].append(date)
            self.save()
    
    def record_weekly_section(self, section_type: str, date: str):
        """Registra que una sección semanal fue usada"""
        if section_type in self.data["weekly_sections"]:
            if date not in self.data["weekly_sections"][section_type]:
                self.data["weekly_sections"][section_type].append(date)
                self.save()
    
    def record_topic(self, topic: str, date: str):
        """Registra que un tema fue mencionado"""
        if topic not in self.data["topics_mentioned"]:
            self.data["topics_mentioned"][topic] = []
        
        if date not in self.data["topics_mentioned"][topic]:
            self.data["topics_mentioned"][topic].append(date)
            self.save()
    
    def record_event(self, event_description: str, date: str):
        """Registra que un evento fue mencionado"""
        # Normalizar descripción (primeros 100 caracteres)
        normalized = event_description[:100]
        if normalized not in self.data["events_mentioned"]:
            self.data["events_mentioned"][normalized] = []
        
        if date not in self.data["events_mentioned"][normalized]:
            self.data["events_mentioned"][normalized].append(date)
            self.save()
    
    def record_news(self, news_title: str, date: str):
        """Registra que una noticia fue mencionada (primeros 50 chars, normalizado)"""
        normalized = _normalize_text(news_title)[:50]
        if not normalized:
            return
        if normalized not in self.data["news_topics"]:
            self.data["news_topics"][normalized] = []

        if date not in self.data["news_topics"][normalized]:
            self.data["news_topics"][normalized].append(date)
            self.save()

    def record_fact(self, fact_text: str, date: str):
        """Registra un dato del día usado"""
        normalized = fact_text[:200]
        if normalized not in self.data["facts_used"]:
            self.data["facts_used"][normalized] = []

        if date not in self.data["facts_used"][normalized]:
            self.data["facts_used"][normalized].append(date)
            self.save()
    
    def get_players_usage_count(self) -> Dict[str, int]:
        """Obtiene conteo de uso de jugadores"""
        return {player: len(dates) for player, dates in self.data["players_used"].items()}
    
    def get_least_used_players(self, available_players: List[Dict], limit: int = 5) -> List[Dict]:
        """Obtiene los jugadores menos usados de una lista"""
        usage = self.get_players_usage_count()
        
        # Agregar jugadores que no están en la base de datos (prioridad máxima)
        player_scores = []
        for player in available_players:
            player_name = player.get("name", "")
            count = usage.get(player_name, 0)
            player_scores.append((count, player))
        
        # Ordenar por uso (menos usado primero)
        player_scores.sort(key=lambda x: x[0])
        
        return [player for _, player in player_scores[:limit]]
    
    def get_section_usage_count(self, section_type: str) -> int:
        """Obtiene cuántas veces se usó una sección"""
        return len(self.data["weekly_sections"].get(section_type, []))
    
    def get_recent_topics(self, days: int = 30) -> List[str]:
        """Obtiene temas mencionados recientemente"""
        cutoff_date = datetime.now().isoformat()[:10]  # YYYY-MM-DD
        # Simplificado: retornar todos los temas
        return list(self.data["topics_mentioned"].keys())
    
    def analyze_report(self, report: Dict):
        """Analiza un informe y registra todo su contenido"""
        date = report.get("date", "")
        if not date:
            return
        
        message = report.get("message", "")
        data = report.get("data", {})
        
        # Determinar tipo de sección según el día
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            weekday = date_obj.weekday()
        except:
            return
        
        # Registrar sección semanal
        if weekday in [0, 4]:  # Lunes, Viernes
            self.record_weekly_section("seleccion_mundiales", date)
        elif weekday in [1, 3]:  # Martes, Jueves
            self.record_weekly_section("jugador_scaloneta", date)
        elif weekday == 5:  # Sábado
            self.record_weekly_section("dato_mundialista", date)
        elif weekday == 6:  # Domingo
            self.record_weekly_section("dato_pais_sede", date)
        
        # Extraer y registrar jugadores mencionados
        players = [
            "Messi", "Di María", "Martínez", "Romero", "De Paul", "Mac Allister",
            "Álvarez", "Lautaro", "Acuña", "Tagliafico", "Molina", "Paredes",
            "Lo Celso", "Palacios", "Garnacho", "Enzo", "Fernández", "Scaloni",
            "Otamendi", "Dibu"
        ]
        for player in players:
            if player.lower() in message.lower():
                self.record_player_used(player, date)
        
        # Registrar eventos
        events = data.get("events", [])
        for event in events:
            desc = event.get("description", "")
            if desc:
                self.record_event(desc, date)
        
        # Registrar noticias (match parcial: primeros 40 chars del titulo normalizado)
        msg_norm = _normalize_text(message)
        news = data.get("news", [])
        for item in news:
            title = item.get("title", "")
            if not title:
                continue
            title_norm = _normalize_text(title)[:40]
            if title_norm and title_norm in msg_norm:
                self.record_news(title, date)

        # Registrar dato del día (si aparece en el mensaje)
        for line in message.splitlines():
            line_strip = line.strip()
            if "dato del día" in line_strip.lower() or "dato del dia" in line_strip.lower():
                # Remover prefijos comunes y guardar el contenido
                cleaned = line_strip
                for prefix in ["📊", "Dato del día:", "Dato del dia:", "Dato del día", "Dato del dia"]:
                    cleaned = cleaned.replace(prefix, "").strip(" :.-")
                if cleaned:
                    self.record_fact(cleaned, date)
                break
        
        # Registrar temas generales
        if "mundial" in message.lower():
            self.record_topic("mundial", date)
        if "selección" in message.lower() or "argentina" in message.lower():
            self.record_topic("seleccion", date)
        if "escaloneta" in message.lower():
            self.record_topic("escaloneta", date)


def build_memory_context_from_db(target_date: str) -> str:
    """Construye contexto de memoria desde la base de datos"""
    db = MemoryDatabase()
    
    # Determinar tipo de sección del día
    try:
        date_obj = datetime.strptime(target_date, "%Y-%m-%d")
        weekday = date_obj.weekday()
    except:
        weekday = None
    
    context_parts = []
    context_parts.append("### Memoria de Contenido Anterior (Base de Datos Persistente)\n")
    context_parts.append(f"Base de datos actualizada: {db.data.get('last_updated', 'N/A')}\n")
    
    # Información específica según el día
    if weekday == 0 or weekday == 4:  # Lunes o Viernes - Selección en Mundiales
        context_parts.append("\n**Sección del día: Selección Argentina en Mundiales**")
        count = db.get_section_usage_count("seleccion_mundiales")
        context_parts.append(f"Esta sección se ha usado {count} veces en total.")
        context_parts.append("Evita repetir los mismos temas, momentos históricos o comparaciones.")
        context_parts.append("Varía el enfoque: si antes hablaste de títulos, ahora habla de participaciones; si antes de 1986, ahora de 2022, etc.")
    
    elif weekday == 1 or weekday == 3:  # Martes o Jueves - Jugador
        context_parts.append("\n**Sección del día: Jugador de la Scaloneta**")
        players_usage = db.get_players_usage_count()
        if players_usage:
            context_parts.append("\nJugadores ya destacados (historial completo):")
            sorted_players = sorted(players_usage.items(), key=lambda x: x[1], reverse=True)
            for player, count in sorted_players[:10]:
                context_parts.append(f"- {player}: {count} vez(es)")
            context_parts.append("\n💡 Prioriza jugadores que NO hayan sido destacados, o si repites uno, busca un ángulo completamente diferente.")
        else:
            context_parts.append("\nNingún jugador ha sido destacado aún. Puedes elegir cualquier jugador.")
    
    elif weekday == 5:  # Sábado - Dato Mundialista
        context_parts.append("\n**Sección del día: Dato Mundialista**")
        count = db.get_section_usage_count("dato_mundialista")
        context_parts.append(f"Esta sección se ha usado {count} veces en total.")
        context_parts.append("Evita repetir los mismos datos, estadísticas o curiosidades.")
        context_parts.append("Busca nuevos ángulos: formato, sedes, récords, historia, etc.")
    
    elif weekday == 6:  # Domingo - País Sede
        context_parts.append("\n**Sección del día: Dato del País Sede**")
        count = db.get_section_usage_count("dato_pais_sede")
        context_parts.append(f"Esta sección se ha usado {count} veces en total.")
        context_parts.append("Varía entre Estados Unidos, Canadá y México, o busca nuevos aspectos de cada país.")
    
    # Información general
    topics = db.get_recent_topics()
    if topics:
        context_parts.append("\n**Temas generales ya cubiertos:**")
        context_parts.append("Asegúrate de variar el enfoque si mencionas estos temas.")

    def _filter_recent_items(items_map: Dict[str, List[str]], days: int = 30) -> List[str]:
        """Retorna claves ordenadas por uso reciente dentro de ventana de dias."""
        cutoff = datetime.now().date()
        recent_items = []
        for key, dates in items_map.items():
            parsed_dates = []
            for d in dates:
                try:
                    parsed_dates.append(datetime.strptime(d, "%Y-%m-%d").date())
                except Exception:
                    continue
            if not parsed_dates:
                continue
            last_date = max(parsed_dates)
            if (cutoff - last_date).days <= days:
                recent_items.append((last_date, key))
        recent_items.sort(key=lambda x: x[0], reverse=True)
        return [key for _, key in recent_items]

    facts_used = db.data.get("facts_used", {})
    if facts_used:
        recent_facts = _filter_recent_items(facts_used, days=30)
        if recent_facts:
            context_parts.append("\n**Datos del día usados recientemente (últimos 30 días):**")
            for fact in recent_facts[:10]:
                context_parts.append(f"- {fact}")
            context_parts.append("Evita repetir estos datos en nuevos informes.")

    news_used = db.data.get("news_topics", {})
    if news_used:
        recent_news = _filter_recent_items(news_used, days=30)
        if recent_news:
            context_parts.append("\n**Noticias usadas recientemente (últimos 30 días):**")
            for title in recent_news[:10]:
                context_parts.append(f"- {title}")
            context_parts.append("Evita repetir estas noticias en nuevos informes.")
    
    context_parts.append("\n**Instrucciones generales:**")
    context_parts.append("- NO repitas exactamente la misma información, datos o frases")
    context_parts.append("- Si mencionas algo similar, busca un ángulo o enfoque completamente diferente")
    context_parts.append("- Varía el vocabulario y las expresiones")
    context_parts.append("- Prioriza información nueva o perspectivas frescas")
    context_parts.append("- Esta base de datos rastrea TODO el historial, no solo los últimos días")
    
    return "\n".join(context_parts)


def update_database_from_reports():
    """Actualiza la base de datos analizando todos los informes existentes"""
    from pathlib import Path
    
    REPORTS_DIR = PROJECT_ROOT / "reports"
    db = MemoryDatabase()
    
    print("🔄 Actualizando base de datos desde informes existentes...")
    
    count = 0
    for report_file in sorted(REPORTS_DIR.glob("*.json")):
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                report = json.load(f)
                db.analyze_report(report)
                count += 1
        except Exception as e:
            print(f"⚠️  Error al procesar {report_file}: {e}")
    
    print(f"✅ Base de datos actualizada: {count} informes procesados")
    print(f"   - Jugadores registrados: {len(db.data['players_used'])}")
    print(f"   - Secciones registradas: {sum(len(v) for v in db.data['weekly_sections'].values())}")
    print(f"   - Temas registrados: {len(db.data['topics_mentioned'])}")


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Base de datos de memoria para evitar repeticiones"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Actualizar base de datos desde informes existentes"
    )
    parser.add_argument(
        "--date",
        help="Fecha objetivo (YYYY-MM-DD). Default: hoy",
        default=datetime.now().strftime("%Y-%m-%d")
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Mostrar contenido de la base de datos"
    )
    
    args = parser.parse_args()
    
    if args.update:
        update_database_from_reports()
        return
    
    if args.show:
        db = MemoryDatabase()
        print("📊 Contenido de la Base de Datos:")
        print("=" * 50)
        print(f"Jugadores registrados: {len(db.data['players_used'])}")
        for player, dates in sorted(db.data['players_used'].items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  - {player}: {len(dates)} vez(es)")
        print(f"\nSecciones usadas:")
        for section_type, dates in db.data['weekly_sections'].items():
            print(f"  - {section_type}: {len(dates)} vez(es)")
        return
    
    # Generar contexto
    print("🧠 Contexto de Memoria desde Base de Datos")
    print("=" * 50)
    print(f"📅 Fecha objetivo: {args.date}\n")
    print(build_memory_context_from_db(args.date))


if __name__ == "__main__":
    main()

