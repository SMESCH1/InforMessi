#!/usr/bin/env python3
"""
Detecta contenido audiovisual para una fecha específica
"""

import json
from pathlib import Path
from typing import Dict, Optional

PROJECT_ROOT = Path(__file__).parent.parent
MEDIA_DIR = PROJECT_ROOT / "assets" / "media"


def get_media_for_date(date: str) -> Optional[Dict]:
    """
    Detecta contenido audiovisual para una fecha específica
    Retorna None si no hay contenido, o dict con información del contenido
    """
    date_dir = MEDIA_DIR / date
    
    if not date_dir.exists():
        return None
    
    # Buscar archivos de imagen
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    images = []
    for ext in image_extensions:
        images.extend(list(date_dir.glob(f"*{ext}")))
        images.extend(list(date_dir.glob(f"*{ext.upper()}")))
    
    # Buscar archivos de video
    video_extensions = ['.mp4', '.mov', '.gif']
    videos = []
    for ext in video_extensions:
        videos.extend(list(date_dir.glob(f"*{ext}")))
        videos.extend(list(date_dir.glob(f"*{ext.upper()}")))
    
    # Cargar metadata si existe
    metadata_file = date_dir / "metadata.json"
    metadata = {}
    if metadata_file.exists():
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        except:
            pass
    
    if not images and not videos:
        return None
    
    return {
        "has_media": True,
        "images": [str(img.relative_to(PROJECT_ROOT)) for img in images],
        "videos": [str(vid.relative_to(PROJECT_ROOT)) for vid in videos],
        "primary_image": str(images[0].relative_to(PROJECT_ROOT)) if images else None,
        "primary_video": str(videos[0].relative_to(PROJECT_ROOT)) if videos else None,
        "metadata": metadata,
        "date": date
    }


def main():
    """Función principal - para testing"""
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(
        description="Detecta contenido audiovisual para una fecha"
    )
    parser.add_argument(
        "--date",
        help="Fecha a verificar (YYYY-MM-DD). Default: hoy"
    )
    
    args = parser.parse_args()
    
    if args.date:
        target_date = args.date
    else:
        target_date = datetime.now().strftime("%Y-%m-%d")
    
    media = get_media_for_date(target_date)
    
    if media:
        print(f"✅ Contenido encontrado para {target_date}:")
        print(f"   Imágenes: {len(media['images'])}")
        print(f"   Videos: {len(media['videos'])}")
        if media['primary_image']:
            print(f"   Imagen principal: {media['primary_image']}")
    else:
        print(f"ℹ️  No hay contenido audiovisual para {target_date}")


if __name__ == "__main__":
    main()

