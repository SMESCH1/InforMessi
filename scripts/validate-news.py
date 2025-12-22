#!/usr/bin/env python3
"""
Script para validar noticias: fecha y contenido obsoleto
Fase 4 - InforMessi
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict

# Palabras clave que indican información obsoleta
OBSOLETE_KEYWORDS = [
    "gerardo martino",
    "tata martino",
    "sampaoli",
    "bauza",
    "maradona dt",  # Maradona como DT (ya no es)
    "batista",
    "sabella",  # A menos que sea histórico
]

# Contextos donde estas palabras son válidas (históricos)
VALID_CONTEXTS = [
    "histórico",
    "historia",
    "recordó",
    "recordar",
    "pasado",
    "anteriormente",
    "en el pasado",
]


def is_news_recent(news_item: Dict, max_days: int = 3) -> bool:
    """Verifica si una noticia es reciente (últimos N días)"""
    published_at = news_item.get("published_at", "")
    if not published_at:
        return False
    
    try:
        # Parsear fecha (puede venir en diferentes formatos)
        if "T" in published_at:
            # Formato ISO: 2025-12-21T13:52:19Z
            date_str = published_at.split("T")[0]
            news_date = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            # Otro formato
            news_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        
        # Calcular diferencia
        today = datetime.now().date()
        news_date_only = news_date.date()
        days_diff = (today - news_date_only).days
        
        return days_diff <= max_days
    except Exception:
        # Si no se puede parsear, asumir que es reciente (mejor incluir que excluir)
        return True


def contains_obsolete_info(news_item: Dict) -> bool:
    """Verifica si la noticia contiene información obsoleta"""
    title = news_item.get("title", "").lower()
    description = news_item.get("description", "").lower()
    text = f"{title} {description}"
    
    # Buscar palabras clave obsoletas
    for keyword in OBSOLETE_KEYWORDS:
        if keyword in text:
            # Verificar si está en contexto histórico válido
            is_historical = any(context in text for context in VALID_CONTEXTS)
            if not is_historical:
                return True
    
    return False


def validate_news(news_list: List[Dict], max_days: int = 3) -> List[Dict]:
    """Valida y filtra noticias por fecha y contenido obsoleto"""
    valid_news = []
    
    for news in news_list:
        # Validar fecha
        if not is_news_recent(news, max_days):
            continue
        
        # Validar contenido obsoleto
        if contains_obsolete_info(news):
            continue
        
        valid_news.append(news)
    
    return valid_news


def main():
    """Función principal para testing"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Valida noticias por fecha y contenido"
    )
    parser.add_argument(
        "--input",
        help="Archivo JSON con noticias"
    )
    parser.add_argument(
        "--max-days",
        type=int,
        default=3,
        help="Días máximos de antigüedad (default: 3)"
    )
    
    args = parser.parse_args()
    
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            news = json.load(f)
    else:
        # Leer desde stdin
        import sys
        news = json.load(sys.stdin)
    
    print(f"📰 Validando {len(news)} noticia(s)...")
    print(f"   Máximo de días: {args.max_days}")
    print()
    
    valid_news = validate_news(news, args.max_days)
    
    print(f"✅ Noticias válidas: {len(valid_news)}")
    print(f"❌ Noticias filtradas: {len(news) - len(valid_news)}")
    print()
    
    if len(news) != len(valid_news):
        print("📋 Noticias filtradas:")
        for news_item in news:
            if news_item not in valid_news:
                print(f"  - {news_item['title'][:60]}...")
                if not is_news_recent(news_item, args.max_days):
                    print(f"    ⚠️  Razón: Noticia muy antigua")
                if contains_obsolete_info(news_item):
                    print(f"    ⚠️  Razón: Contiene información obsoleta")
    
    # Retornar JSON
    print(json.dumps(valid_news, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

