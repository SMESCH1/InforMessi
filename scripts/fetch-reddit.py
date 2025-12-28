#!/usr/bin/env python3
"""
Scrapea Reddit para obtener posts relevantes sobre la selección argentina,
el Mundial 2026, la Liga Profesional y jugadores de la selección
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

PROJECT_ROOT = Path(__file__).parent.parent

# Subreddits a monitorear
SUBREDDITS = [
    "soccer",           # Fútbol general
    "argentina",        # Argentina general (puede tener contenido de fútbol)
    "fulbo",            # Fútbol argentino
    "worldcup",         # Mundial
    "messi",            # Messi específico
]

# Palabras clave para filtrar posts relevantes
KEYWORDS = [
    "argentina", "seleccion argentina", "scaloneta",
    "messi", "di maria", "martinez", "de paul", "mac allister",
    "mundial 2026", "world cup 2026", "qatar 2022",
    "liga profesional", "superliga", "primera division argentina",
    "afa", "scaloni", "campeon del mundo"
]


def fetch_reddit_posts_praw(subreddits: List[str], limit: int = 10) -> List[Dict]:
    """
    Obtiene posts de Reddit usando PRAW (Python Reddit API Wrapper)
    Requiere: pip install praw
    """
    try:
        import praw
    except ImportError:
        print("⚠️  PRAW no instalado. Instala con: pip install praw")
        return []
    
    # Configurar cliente Reddit
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID", ""),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET", ""),
        user_agent=os.getenv("REDDIT_USER_AGENT", "InforMessi/1.0")
    )
    
    if not reddit.read_only:
        print("⚠️  Reddit no configurado correctamente")
        return []
    
    posts = []
    cutoff_date = datetime.now() - timedelta(days=3)  # Solo últimos 3 días
    
    for subreddit_name in subreddits:
        try:
            subreddit = reddit.subreddit(subreddit_name)
            
            for post in subreddit.hot(limit=limit):
                # Verificar fecha (últimos 3 días)
                post_date = datetime.fromtimestamp(post.created_utc)
                if post_date < cutoff_date:
                    continue
                
                # Verificar relevancia por keywords
                title_lower = post.title.lower()
                selftext_lower = (post.selftext or "").lower()
                
                is_relevant = any(
                    keyword.lower() in title_lower or keyword.lower() in selftext_lower
                    for keyword in KEYWORDS
                )
                
                if is_relevant:
                    posts.append({
                        "title": post.title,
                        "content": post.selftext[:500] if post.selftext else "",
                        "url": f"https://reddit.com{post.permalink}",
                        "subreddit": subreddit_name,
                        "score": post.score,
                        "comments": post.num_comments,
                        "author": str(post.author) if post.author else "[deleted]",
                        "created_at": datetime.fromtimestamp(post.created_utc).isoformat(),
                        "source": "Reddit"
                    })
        except Exception as e:
            print(f"⚠️  Error al obtener posts de r/{subreddit_name}: {e}")
            continue
    
    return posts


def fetch_reddit_posts_scraping(subreddits: List[str], limit: int = 10) -> List[Dict]:
    """
    Obtiene posts de Reddit usando scraping directo (sin API)
    Alternativa si no quieres configurar PRAW
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("⚠️  requests/BeautifulSoup no instalado")
        return []
    
    posts = []
    cutoff_date = datetime.now() - timedelta(days=3)
    
    for subreddit_name in subreddits:
        try:
            # Reddit JSON endpoint (sin autenticación)
            url = f"https://www.reddit.com/r/{subreddit_name}/hot.json?limit={limit}"
            headers = {
                "User-Agent": os.getenv("REDDIT_USER_AGENT", "InforMessi/1.0")
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                continue
            
            data = response.json()
            
            for post_data in data.get("data", {}).get("children", [])[:limit]:
                post = post_data.get("data", {})
                
                # Verificar fecha
                post_date = datetime.fromtimestamp(post.get("created_utc", 0))
                if post_date < cutoff_date:
                    continue
                
                # Verificar relevancia
                title = post.get("title", "").lower()
                selftext = (post.get("selftext", "") or "").lower()
                
                is_relevant = any(
                    keyword.lower() in title or keyword.lower() in selftext
                    for keyword in KEYWORDS
                )
                
                if is_relevant:
                    posts.append({
                        "title": post.get("title", ""),
                        "content": (post.get("selftext", "") or "")[:500],
                        "url": f"https://reddit.com{post.get('permalink', '')}",
                        "subreddit": subreddit_name,
                        "score": post.get("score", 0),
                        "comments": post.get("num_comments", 0),
                        "author": post.get("author", "[deleted]"),
                        "created_at": datetime.fromtimestamp(post.get("created_utc", 0)).isoformat(),
                        "source": "Reddit"
                    })
        except Exception as e:
            print(f"⚠️  Error al obtener posts de r/{subreddit_name}: {e}")
            continue
    
    return posts


def fetch_reddit_posts(max_results: int = 5, silent: bool = False) -> List[Dict]:
    """
    Obtiene posts relevantes de Reddit
    Intenta usar PRAW primero, luego scraping como fallback
    """
    if not silent:
        print("🔍 Buscando posts relevantes en Reddit...")
    
    # Intentar con PRAW (si está configurado)
    if os.getenv("REDDIT_CLIENT_ID"):
        posts = fetch_reddit_posts_praw(SUBREDDITS, limit=max_results * 2)
    else:
        # Usar scraping directo
        posts = fetch_reddit_posts_scraping(SUBREDDITS, limit=max_results * 2)
    
    # Ordenar por score y relevancia
    posts.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    # Limitar resultados
    posts = posts[:max_results]
    
    if not silent:
        print(f"✅ Encontrados {len(posts)} posts relevantes de Reddit")
    
    return posts


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Obtiene posts relevantes de Reddit"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Máximo número de posts a obtener (default: 5)"
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Solo imprimir JSON (para integración con otros scripts)"
    )
    
    args = parser.parse_args()
    
    posts = fetch_reddit_posts(args.max_results, silent=args.json_only)
    
    if args.json_only:
        print(json.dumps(posts, indent=2, ensure_ascii=False))
    else:
        print(f"\n📊 Posts encontrados: {len(posts)}\n")
        for i, post in enumerate(posts, 1):
            print(f"{i}. r/{post['subreddit']}: {post['title']}")
            print(f"   Score: {post['score']} | Comentarios: {post['comments']}")
            print(f"   URL: {post['url']}\n")


if __name__ == "__main__":
    main()

